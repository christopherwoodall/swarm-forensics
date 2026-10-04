"""Swarm Forensics case management: entities, relationships, indicators.

The case DB is the system of record for the analyst's workspace:
entities (traces, agents, swarms, collections), the links between
them, and indicators extracted from trace text. Hunts, the IOC
list, and review decisions keep their existing JSONL stores
(state/jobs/, state/hits/, state/iocs.json, state/review.json);
the DB links to them by id (a trace entity stores its hunt job id
in data_json).

SAFETY INVARIANT (keep closed: adversarial #2): extracted
indicators are NOT IOCs. Extraction populates the case DB only.
Promotion to the IOC list still requires a human decision in the
review queue (iocs.py). No function in this module touches the
IOC list. The indicator table has no promotion path.

SECURITY INVARIANT: all SQL uses parameter placeholders (?). No
string interpolation into SQL statements, ever. Trace text is
untrusted; it enters only as bound parameters.

Stdlib only. No network. Indicator extraction is pure regex.
"""

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DB_NAME = "swarm-forensics.db"

# Current schema version. migrate() applies every migration below it.
SCHEMA_VERSION = 1

ENTITY_TYPES = ("trace", "agent", "swarm", "collection")
REL_KINDS = ("trace_of", "member_of", "part_of", "related")
INDICATOR_KINDS = ("url", "domain", "nonce", "relay", "hash")


def _utcnow():
    return datetime.now(timezone.utc).isoformat()


def connect(path=None, cfg=None):
    """Open the case DB and migrate it. Give path or cfg, not both.

    With cfg, the DB lives at <state_dir>/swarm-forensics.db (config.state_path).
    Every caller gets a migrated schema: connect() always runs migrate().
    """
    if path is None and cfg is None:
        raise ValueError("connect needs a path or a cfg")
    if path is None:
        from config import state_path
        path = state_path(cfg, DB_NAME)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    migrate(conn)
    return conn


# ---------------------------------------------------------------------------
# Schema and migrations. DDL is duplicated in SPEC.md; this module is
# authoritative for the code. migrate() reads schema_version and applies
# each numbered migration in order. A DB without the version table is
# treated as version 0.
# ---------------------------------------------------------------------------

_MIGRATIONS = []


def _migration(from_version):
    def deco(fn):
        _MIGRATIONS.append((from_version, fn))
        return fn
    return deco


@_migration(0)
def _migrate_0_to_1(conn):
    """v1: full case schema.

    An existing pre-migration entities table (id, type, label only)
    keeps its rows; missing columns are added, not rebuilt.
    """
    # -- entities -----------------------------------------------------------
    cols = {r[1] for r in conn.execute("PRAGMA table_info(entities)")}
    if not cols:
        conn.execute(
            """CREATE TABLE entities(
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL CHECK(type IN ('trace','agent','swarm','collection')),
                label TEXT NOT NULL,
                data_json TEXT,
                provenance TEXT,
                created_utc TEXT NOT NULL)""")
    else:
        if "data_json" not in cols:
            conn.execute("ALTER TABLE entities ADD COLUMN data_json TEXT")
        if "provenance" not in cols:
            conn.execute("ALTER TABLE entities ADD COLUMN provenance TEXT")
        if "created_utc" not in cols:
            conn.execute("ALTER TABLE entities ADD COLUMN created_utc TEXT")
    # -- relationships ------------------------------------------------------
    conn.execute(
        """CREATE TABLE IF NOT EXISTS relationships(
            id TEXT PRIMARY KEY,
            from_id TEXT NOT NULL,
            to_id TEXT NOT NULL,
            rel TEXT NOT NULL
                CHECK(rel IN ('trace_of','member_of','part_of','related')),
            created_utc TEXT NOT NULL)""")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_rel_from ON relationships(from_id)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_rel_to ON relationships(to_id)")
    # -- indicators ---------------------------------------------------------
    conn.execute(
        """CREATE TABLE IF NOT EXISTS indicators(
            id TEXT PRIMARY KEY,
            trace_id TEXT NOT NULL,
            kind TEXT NOT NULL
                CHECK(kind IN ('url','domain','nonce','relay','hash')),
            value TEXT NOT NULL,
            created_utc TEXT NOT NULL)""")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ind_trace ON indicators(trace_id)")
    # -- version ------------------------------------------------------------
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version(version INT NOT NULL)")
    if not conn.execute("SELECT version FROM schema_version").fetchone():
        conn.execute("INSERT INTO schema_version(version) VALUES (1)")


def migrate(conn):
    """Apply pending migrations. Idempotent. Returns the final version."""
    row = None
    try:
        row = conn.execute("SELECT version FROM schema_version").fetchone()
    except sqlite3.OperationalError:
        row = None  # no version table yet: version 0
    version = row[0] if row else 0
    for from_version, fn in sorted(_MIGRATIONS):
        if from_version >= version:
            fn(conn)
            version = from_version + 1
            conn.execute("UPDATE schema_version SET version = ?",
                         (version,))
    conn.commit()
    return version


def _new_id():
    return uuid.uuid4().hex


def _entity_row(r):
    if r is None:
        return None
    data = None
    if r["data_json"]:
        try:
            data = json.loads(r["data_json"])
        except json.JSONDecodeError:
            data = None
    return {"id": r["id"], "type": r["type"], "label": r["label"],
            "data": data, "provenance": r["provenance"] or "",
            "created_utc": r["created_utc"]}


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------

def add_entity(conn, type, label, data=None, provenance=""):
    """Insert one entity. Raises ValueError on a bad type."""
    if type not in ENTITY_TYPES:
        raise ValueError(f"bad entity type {type!r}; want one of "
                         f"{ENTITY_TYPES}")
    label = (label or "").strip()
    if not label:
        raise ValueError("entity label is required")
    eid = _new_id()
    conn.execute(
        "INSERT INTO entities(id, type, label, data_json, provenance,"
        " created_utc) VALUES (?,?,?,?,?,?)",
        (eid, type, label,
         json.dumps(data) if data is not None else None,
         provenance or "", _utcnow()))
    conn.commit()
    return eid


def get_entity(conn, id):
    """Return the entity dict, or None."""
    return _entity_row(conn.execute(
        "SELECT * FROM entities WHERE id = ?", (id,)).fetchone())


def list_entities(conn, type=None):
    """List entities, newest first. Optional type filter."""
    if type is not None and type not in ENTITY_TYPES:
        raise ValueError(f"bad entity type {type!r}")
    if type:
        rows = conn.execute(
            "SELECT * FROM entities WHERE type = ?"
            " ORDER BY created_utc DESC", (type,))
    else:
        rows = conn.execute("SELECT * FROM entities ORDER BY created_utc DESC")
    return [_entity_row(r) for r in rows]


def update_entity(conn, id, label=None, data=None, provenance=None):
    """Update the given fields. Returns True when the entity exists."""
    sets, vals = [], []
    if label is not None:
        sets.append("label = ?")
        vals.append(label.strip())
    if data is not None:
        sets.append("data_json = ?")
        vals.append(json.dumps(data))
    if provenance is not None:
        sets.append("provenance = ?")
        vals.append(provenance or "")
    if not sets:
        return get_entity(conn, id) is not None
    vals.append(id)
    cur = conn.execute(f"UPDATE entities SET {', '.join(sets)} WHERE id = ?",
                       vals)
    conn.commit()
    return cur.rowcount > 0


def delete_entity(conn, id):
    """Delete the entity, its relationships, and its indicators.

    The IOC list is never touched: it lives in state/iocs.json and
    this DB holds no reference to it. Deletion cannot promote,
    demote, or remove an IOC.
    """
    conn.execute("DELETE FROM indicators WHERE trace_id = ?", (id,))
    conn.execute(
        "DELETE FROM relationships WHERE from_id = ? OR to_id = ?", (id, id))
    cur = conn.execute("DELETE FROM entities WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------

def link(conn, from_id, to_id, rel):
    """Link two entities. Both must exist. Raises ValueError otherwise."""
    if rel not in REL_KINDS:
        raise ValueError(f"bad rel {rel!r}; want one of {REL_KINDS}")
    if not get_entity(conn, from_id):
        raise ValueError(f"unknown entity {from_id!r}")
    if not get_entity(conn, to_id):
        raise ValueError(f"unknown entity {to_id!r}")
    lid = _new_id()
    conn.execute(
        "INSERT INTO relationships(id, from_id, to_id, rel, created_utc)"
        " VALUES (?,?,?,?,?)",
        (lid, from_id, to_id, rel, _utcnow()))
    conn.commit()
    return lid


def unlink(conn, id):
    """Remove one relationship by its id. Returns True when found."""
    cur = conn.execute("DELETE FROM relationships WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _link_row(r):
    return {"id": r["id"], "from_id": r["from_id"], "to_id": r["to_id"],
            "rel": r["rel"], "created_utc": r["created_utc"]}


def neighbors(conn, id):
    """The entity, its links (both directions), and adjacent entities."""
    entity = get_entity(conn, id)
    if entity is None:
        return None
    rows = conn.execute(
        "SELECT * FROM relationships WHERE from_id = ? OR to_id = ?"
        " ORDER BY created_utc", (id, id))
    links = [_link_row(r) for r in rows]
    other = {r["to_id"] if r["from_id"] == id else r["from_id"]
             for r in links}
    adj = {}
    for oid in other:
        e = get_entity(conn, oid)
        if e:
            adj[oid] = e
    return {"entity": entity, "links": links, "adjacent": adj}


def graph(conn):
    """Full graph for the Obsidian-style view: nodes and edges."""
    nodes = [{"id": r["id"], "type": r["type"], "label": r["label"]}
             for r in conn.execute(
                 "SELECT id, type, label FROM entities")]
    edges = [_link_row(r) for r in conn.execute("SELECT * FROM relationships")]
    return {"nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Indicator extraction. Pure regex, no network, no model.
# Indicators land in the case DB only. They are NOT IOCs.
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://[^\s<>\"']+")
_ZZ_OAI_RE = re.compile(r"\bzz=oai\d+")
_ZZBULK_RE = re.compile(r"\bzzbulk=[0-9A-Za-z]{4,}")
_PREPNONCE_RE = re.compile(r"\bprepnonce=[0-9A-Fa-f]{4,}")
_FRESH_RE = re.compile(r"\bfresh=x\d+\.\d+")
_MD5_RE = re.compile(r"\b[0-9a-fA-F]{32}\b")
_SHA1_RE = re.compile(r"\b[0-9a-fA-F]{40}\b")
_SHA256_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")

# Fallback relay hosts, from predict.py's fallback slot list.
# The live inventory comes from the grammar file when present.
_RELAY_FALLBACK = ["jqp.vercel.app", "allorigins.hexlet.app", "r.jina.ai"]


def _relay_inventory():
    """Relay hosts from predict.py's grammar inventory, else fallback."""
    try:
        from predict import _load_grammar, _slots_from_grammar
        g = _load_grammar()
        if g:
            return _slots_from_grammar(g)["relays"] or _RELAY_FALLBACK
    except (ImportError, KeyError, TypeError):
        pass
    return _RELAY_FALLBACK


def _clean_url(u):
    return u.rstrip(".,;:!?)'\"")


def extract_indicators(trace_text):
    """Extract (kind, value) pairs from trace text.

    Kinds: url, domain, nonce, relay, hash. Order follows first
    appearance in the text; duplicates collapse. Pure regex.
    """
    text = trace_text or ""
    found = []  # (offset, kind, value)

    for m in _URL_RE.finditer(text):
        url = _clean_url(m.group(0))
        if not url:
            continue
        found.append((m.start(), "url", url))
        try:
            host = urlparse(url).hostname
        except ValueError:
            host = None
        if host:
            found.append((m.start(), "domain", host.lower()))

    for rx in (_ZZ_OAI_RE, _ZZBULK_RE, _PREPNONCE_RE, _FRESH_RE):
        for m in rx.finditer(text):
            found.append((m.start(), "nonce", m.group(0)))

    for host in _relay_inventory():
        pos = 0
        while True:
            i = text.find(host, pos)
            if i < 0:
                break
            found.append((i, "relay", host))
            pos = i + len(host)

    for rx in (_SHA256_RE, _SHA1_RE, _MD5_RE):
        for m in rx.finditer(text):
            found.append((m.start(), "hash", m.group(0).lower()))

    found.sort(key=lambda t: t[0])
    seen = set()
    out = []
    for _, kind, value in found:
        key = (kind, value)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def add_indicator(conn, trace_id, kind, value):
    """Attach one indicator to a trace entity. Raises ValueError on misuse."""
    if kind not in INDICATOR_KINDS:
        raise ValueError(f"bad indicator kind {kind!r}")
    ent = get_entity(conn, trace_id)
    if ent is None or ent["type"] != "trace":
        raise ValueError("indicators attach to trace entities only")
    iid = _new_id()
    conn.execute(
        "INSERT INTO indicators(id, trace_id, kind, value, created_utc)"
        " VALUES (?,?,?,?,?)",
        (iid, trace_id, kind, value, _utcnow()))
    conn.commit()
    return iid


def list_indicators(conn, trace_id):
    """Indicators for one trace, in extraction order."""
    rows = conn.execute(
        "SELECT kind, value FROM indicators WHERE trace_id = ?"
        " ORDER BY created_utc, id", (trace_id,))
    return [{"kind": r["kind"], "value": r["value"]} for r in rows]


def add_trace(conn, label, trace_text, provenance="", job_id=None):
    """Add a trace entity and run indicator extraction automatically.

    The trace text lands in data_json; the hunt job id (when given)
    links back to state/jobs/. Extraction populates the case DB
    only; it never touches the IOC list (see module docstring).
    Returns the entity id.
    """
    data = {"trace_text": trace_text}
    if job_id:
        data["job_id"] = job_id
    eid = add_entity(conn, "trace", label, data=data,
                     provenance=provenance)
    for kind, value in extract_indicators(trace_text):
        add_indicator(conn, eid, kind, value)
    return eid
