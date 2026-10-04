"""One-time import of state from the first (CLI-era) version.

Reads the old JSON, JSONL, and case database. Never modifies or deletes
the old files. Idempotent: each source directory is imported once.
"""

import json
import sqlite3
from pathlib import Path

from . import db
from .paths import PACKAGE_DIR, hermes_home
from .safety import content_hash, redact_text, redact_url

_STATUS = {"active": "active", "proposed": "proposed", "quarantined": "proposed",
           "inactive": "inactive"}
_REL = {"trace_of": "trace_of", "member_of": "member_of", "part_of": "part_of",
        "related": "related"}


def find_state_dirs():
    """Return legacy state directories that exist on this machine."""
    roots = [PACKAGE_DIR.parent, hermes_home() / "plugins" / "swarm-forensics"]
    skills = hermes_home() / "skills"
    if skills.is_dir():
        roots += [p.parent for p in skills.glob("**/swarm-forensics/SKILL.md")]
    found = []
    for root in roots:
        state = Path(root) / "state"
        if state.is_dir() and (state / "iocs.json").exists() \
                and state not in found:
            found.append(state)
    return found


def _read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def import_state(database, state_dir):
    """Import one legacy state directory. Returns a dict of counts."""
    state = Path(state_dir).resolve()
    key = str(state)
    counts = {"iocs": 0, "evidence": 0, "entities": 0, "links": 0,
              "indicators": 0}
    with database.connect() as conn:
        if conn.execute("SELECT 1 FROM cursors WHERE source = 'legacy' AND key = ?",
                        (key,)).fetchone():
            return dict(counts, skipped=True)
        stamp = db.now()
        for rec in _read_json(state / "iocs.json", []):
            term = str(rec.get("term") or "").strip()
            if not term:
                continue
            status = _STATUS.get(rec.get("status"), "proposed")
            cur = conn.execute(
                "INSERT OR IGNORE INTO iocs(term, category, status, origin,"
                " provenance, note, added_utc, updated_utc)"
                " VALUES (?,?,?, 'legacy', ?, ?, ?, ?)",
                (term, str(rec.get("category") or "proposed"), status,
                 str(rec.get("provenance") or "")[:500],
                 str(rec.get("note") or "")[:500],
                 str(rec.get("added_utc") or stamp), stamp))
            counts["iocs"] += cur.rowcount
            if not cur.rowcount and status == "inactive":
                conn.execute("UPDATE iocs SET status = 'inactive', updated_utc = ?"
                             " WHERE term = ? AND status = 'active'", (stamp, term))
        for path in sorted((state / "hits").glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    hit = json.loads(line)
                except ValueError:
                    continue
                url = redact_url(str(hit.get("url") or ""))
                if not url:
                    continue
                excerpt = redact_text(hit.get("evidence"))[:2000]
                cur = conn.execute(
                    "INSERT OR IGNORE INTO evidence(source, query, url, title,"
                    " excerpt, content_hash, observed_utc) VALUES (?,?,?,?,?,?,?)",
                    (str(hit.get("source") or "legacy"),
                     str(hit.get("query_id") or "")[:300], url[:2000],
                     str(hit.get("term") or "")[:300], excerpt,
                     content_hash(excerpt or url),
                     str(hit.get("observed_utc") or stamp)))
                counts["evidence"] += cur.rowcount
        _import_cases(conn, state / "swarm-forensics.db", counts, stamp)
        conn.execute("INSERT INTO cursors(source, key, value) VALUES ('legacy',?,?)",
                     (key, stamp))
    return counts


def _import_cases(conn, path, counts, stamp):
    if not path.exists():
        return
    old = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
    old.row_factory = sqlite3.Row
    try:
        ids = {}
        for row in old.execute("SELECT * FROM entities"):
            name, n = str(row["label"] or row["id"])[:110], 1
            while conn.execute("SELECT 1 FROM entities WHERE type = ? AND name = ?",
                               (row["type"], name)).fetchone():
                n += 1
                name = "%s (%d)" % (str(row["label"])[:100], n)
            new = db.new_id()
            ids[row["id"]] = new
            conn.execute(
                "INSERT INTO entities(id, type, name, attrs, origin, created_utc,"
                " updated_utc) VALUES (?,?,?,?, 'legacy', ?, ?)",
                (new, row["type"], name, row["data_json"] or "{}",
                 row["created_utc"] or stamp, stamp))
            counts["entities"] += 1
        for row in old.execute("SELECT * FROM relationships"):
            src, dst = ids.get(row["from_id"]), ids.get(row["to_id"])
            if src and dst and src != dst:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO links(src, dst, kind, created_utc)"
                    " VALUES (?,?,?,?)",
                    (src, dst, _REL.get(row["rel"], "related"), stamp))
                counts["links"] += cur.rowcount
        for row in old.execute("SELECT * FROM indicators"):
            ent = ids.get(row["trace_id"])
            if ent:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO indicators(entity_id, kind, value,"
                    " first_seen_utc) VALUES (?,?,?,?)",
                    (ent, row["kind"], row["value"], stamp))
                counts["indicators"] += cur.rowcount
    except sqlite3.Error:
        pass  # A damaged old database must not block startup.
    finally:
        old.close()
