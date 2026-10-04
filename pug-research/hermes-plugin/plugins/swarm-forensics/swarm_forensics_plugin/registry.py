"""Operator-editable index sources, URL grammar, and wordlist imports.

The database stores sources and grammar hypotheses. Index fetches only
target hosts of enabled index sources. Every mutation writes an audit event.
"""

from urllib.parse import urlsplit

from . import db
from .iocs import parse_wordlist
from .safety import UrlRefused, validate_url

ADAPTER_KINDS = ("cdx", "urlquery")
GRAMMAR_KINDS = ("pattern", "relay", "nonce_probe", "jq_probe", "target")
CONFIG_ALLOWED_KEYS = {"filter_field", "nonce_prefix"}

DEFAULT_SOURCES = [
    {
        "name": "Wayback CDX",
        "kind": "cdx",
        "endpoint": "https://web.archive.org/cdx/search/cdx",
        "config": {"filter_field": "urlkey", "nonce_prefix": "r.jina.ai/http*"},
        "enabled": 1,
        "probe_candidates": 1,
        "note": "Internet Archive Wayback Machine CDX API",
    },
    {
        "name": "Arquivo.pt",
        "kind": "cdx",
        "endpoint": "https://arquivo.pt/wayback/cdx",
        "config": {"filter_field": "original", "nonce_prefix": "r.jina.ai/http*"},
        "enabled": 1,
        "probe_candidates": 0,
        "note": "Portuguese web archive CDX API",
    },
    {
        "name": "urlquery.net",
        "kind": "urlquery",
        "endpoint": "https://urlquery.net/api/v1/search",
        "config": {},
        "enabled": 0,
        "probe_candidates": 0,
        "note": "endpoint returns 404 (2026-10-04)",
    },
    {
        "name": "Common Crawl",
        "kind": "cdx",
        "endpoint": "https://index.commoncrawl.org/CC-MAIN-2024-10-index",
        "config": {"filter_field": "url"},
        "enabled": 0,
        "probe_candidates": 0,
        "note": "Common Crawl CDX index (update collection ID as needed)",
    },
]

DEFAULT_PATTERNS = [
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zz={text}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zzbulk={text}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&prepnonce={text}&survey_Year_Key={int}",
    "https://jqp.vercel.app/api/v0?jq={long}&url={url}",
    "https://www.sec.gov/files/county.json",
    "https://api.datausa.io/tesseract/data.jsonrecords"
    "?cube={text}&drilldowns={text}&include={long}&measures={text}",
]

DEFAULT_RELAYS = [
    ("https://jqp.vercel.app/api/v0", "query", "jqp.vercel.app"),
    ("https://allorigins.hexlet.app/raw", "query", "allorigins.hexlet.app"),
    ("https://r.jina.ai/", "path", "r.jina.ai"),
]

DEFAULT_NONCE_PROBES = [
    ("oai17816846804506724", "zz"),
    ("1781639035965977052", "zzbulk"),
    ("a94a8fe5ccb19ba61", "prepnonce"),
]

DEFAULT_JQ_PROBES = [
    ".code",
    ".regCF_county_2019",
    'select(test("us-ma-"))',
]

DEFAULT_TARGETS = [
    "https://www.sec.gov/files/regcf.json",
]


class RegistryError(ValueError):
    pass


def _row(row):
    return {k: row[k] for k in row.keys()}


class Registry:
    def __init__(self, database, ledger=None):
        self.db = database
        self.ledger = ledger
        self.seed()

    def _event(self, message, level="info", data=None):
        if self.ledger is not None:
            self.ledger.event(None, "registry", message, level=level, data=data)

    # -- seed ---------------------------------------------------------------

    def seed(self):
        """Seed default sources and grammar rows once."""
        stamp = db.now()
        with self.db.connect() as conn:
            done = conn.execute(
                "SELECT 1 FROM cursors WHERE source = 'meta' AND key = 'registry_seeded'"
            ).fetchone()
            if done:
                return
            for s in DEFAULT_SOURCES:
                conn.execute(
                    "INSERT OR IGNORE INTO index_sources("
                    "name, kind, endpoint, config, enabled, probe_candidates, origin, note,"
                    " created_utc, updated_utc) VALUES (?,?,?,?,?,?,'seed',?,?,?)",
                    (s["name"], s["kind"], s["endpoint"], db.dumps(s["config"]),
                     s["enabled"], s["probe_candidates"], s["note"], stamp, stamp))
            for pat in DEFAULT_PATTERNS:
                conn.execute(
                    "INSERT OR IGNORE INTO url_grammar(kind, value, param, enabled, origin, created_utc)"
                    " VALUES ('pattern', ?, '', 1, 'seed', ?)", (pat, stamp))
            for val, param, _note in DEFAULT_RELAYS:
                conn.execute(
                    "INSERT OR IGNORE INTO url_grammar(kind, value, param, enabled, origin, created_utc)"
                    " VALUES ('relay', ?, ?, 1, 'seed', ?)", (val, param, stamp))
            for val, param in DEFAULT_NONCE_PROBES:
                conn.execute(
                    "INSERT OR IGNORE INTO url_grammar(kind, value, param, enabled, origin, created_utc)"
                    " VALUES ('nonce_probe', ?, ?, 1, 'seed', ?)", (val, param, stamp))
            for val in DEFAULT_JQ_PROBES:
                conn.execute(
                    "INSERT OR IGNORE INTO url_grammar(kind, value, param, enabled, origin, created_utc)"
                    " VALUES ('jq_probe', ?, '', 1, 'seed', ?)", (val, stamp))
            for val in DEFAULT_TARGETS:
                conn.execute(
                    "INSERT OR IGNORE INTO url_grammar(kind, value, param, enabled, origin, created_utc)"
                    " VALUES ('target', ?, '', 1, 'seed', ?)", (val, stamp))
            conn.execute(
                "INSERT INTO cursors(source, key, value) VALUES ('meta', 'registry_seeded', ?)",
                (stamp,))

    # -- index sources ------------------------------------------------------

    def sources(self, enabled_only=False):
        sql = "SELECT * FROM index_sources"
        if enabled_only:
            sql += " WHERE enabled = 1"
        sql += " ORDER BY id"
        with self.db.connect() as conn:
            rows = conn.execute(sql).fetchall()
        out = []
        for r in rows:
            d = _row(r)
            d["config"] = db.loads(d["config"], {})
            out.append(d)
        return out

    def get_source(self, sid):
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM index_sources WHERE id = ?", (sid,)).fetchone()
        if not row:
            return None
        d = _row(row)
        d["config"] = db.loads(d["config"], {})
        return d

    def allowed_hosts(self):
        hosts = set()
        for s in self.sources(enabled_only=True):
            try:
                h = urlsplit(s["endpoint"]).hostname
                if h:
                    hosts.add(h.lower())
            except Exception:
                pass
        return hosts

    def candidate_prober(self):
        """Return the source flagged to probe predicted candidate URLs, or None."""
        sources = self.sources(enabled_only=True)
        for s in sources:
            if s.get("probe_candidates"):
                return s
        return sources[0] if sources else None

    def add_source(self, name, kind, endpoint, config=None, note=""):
        name = str(name or "").strip()
        if not name or len(name) > 80:
            raise RegistryError("source name must be 1 to 80 characters")
        if kind not in ADAPTER_KINDS:
            raise RegistryError("kind must be one of %s" % ", ".join(ADAPTER_KINDS))
        try:
            valid_url = validate_url(endpoint)
        except UrlRefused as exc:
            raise RegistryError("invalid endpoint URL: %s" % exc)
        parts = urlsplit(valid_url)
        if parts.scheme != "https":
            raise RegistryError("endpoint must use https")

        cfg = config or {}
        if not isinstance(cfg, dict):
            raise RegistryError("config must be a dictionary")
        bad_keys = set(cfg.keys()) - CONFIG_ALLOWED_KEYS
        if bad_keys:
            raise RegistryError("unknown config keys: %s" % ", ".join(bad_keys))

        stamp = db.now()
        with self.db.connect() as conn:
            clash = conn.execute("SELECT 1 FROM index_sources WHERE name = ?", (name,)).fetchone()
            if clash:
                raise RegistryError("a source with that name already exists")
            cur = conn.execute(
                "INSERT INTO index_sources(name, kind, endpoint, config, enabled,"
                " probe_candidates, origin, note, created_utc, updated_utc)"
                " VALUES (?,?,?,?, 1, 0, 'human', ?, ?, ?)",
                (name, kind, valid_url, db.dumps(cfg), str(note or "")[:500], stamp, stamp))
            sid = cur.lastrowid
        self._event("added source %s (%s: %s)" % (name, kind, valid_url))
        return self.get_source(sid)

    def update_source(self, sid, **fields):
        source = self.get_source(sid)
        if not source:
            raise RegistryError("source not found")
        updates, args = [], []
        if "enabled" in fields:
            val = 1 if fields["enabled"] else 0
            updates.append("enabled = ?")
            args.append(val)
        if "probe_candidates" in fields:
            val = 1 if fields["probe_candidates"] else 0
            updates.append("probe_candidates = ?")
            args.append(val)
        if "note" in fields:
            updates.append("note = ?")
            args.append(str(fields["note"] or "")[:500])
        if "endpoint" in fields:
            try:
                valid_url = validate_url(fields["endpoint"])
            except UrlRefused as exc:
                raise RegistryError("invalid endpoint URL: %s" % exc)
            if urlsplit(valid_url).scheme != "https":
                raise RegistryError("endpoint must use https")
            updates.append("endpoint = ?")
            args.append(valid_url)
        if "config" in fields:
            cfg = fields["config"] or {}
            if not isinstance(cfg, dict):
                raise RegistryError("config must be a dictionary")
            bad = set(cfg.keys()) - CONFIG_ALLOWED_KEYS
            if bad:
                raise RegistryError("unknown config keys: %s" % ", ".join(bad))
            updates.append("config = ?")
            args.append(db.dumps(cfg))

        if not updates:
            return source

        stamp = db.now()
        updates.append("updated_utc = ?")
        args.append(stamp)
        args.append(sid)

        with self.db.connect() as conn:
            if fields.get("probe_candidates"):
                conn.execute("UPDATE index_sources SET probe_candidates = 0 WHERE id != ?", (sid,))
            conn.execute("UPDATE index_sources SET " + ", ".join(updates) + " WHERE id = ?", args)

        self._event("updated source #%d (%s)" % (sid, ", ".join(fields.keys())))
        return self.get_source(sid)

    def delete_source(self, sid):
        source = self.get_source(sid)
        if not source:
            return False
        with self.db.connect() as conn:
            cur = conn.execute("DELETE FROM index_sources WHERE id = ?", (sid,))
        if cur.rowcount > 0:
            self._event("deleted source %s" % source["name"])
            return True
        return False

    # -- URL grammar --------------------------------------------------------

    def grammar(self, kind=None):
        sql = "SELECT * FROM url_grammar"
        args = []
        if kind:
            if kind not in GRAMMAR_KINDS:
                raise RegistryError("unknown grammar kind: %s" % kind)
            sql += " WHERE kind = ?"
            args.append(kind)
        sql += " ORDER BY id"
        with self.db.connect() as conn:
            return [_row(r) for r in conn.execute(sql, args).fetchall()]

    def add_grammar(self, kind, value, param="", note=""):
        if kind not in GRAMMAR_KINDS:
            raise RegistryError("kind must be one of %s" % ", ".join(GRAMMAR_KINDS))
        value = str(value or "").strip()
        if not value or len(value) > 600:
            raise RegistryError("value must be 1 to 600 characters")
        param = str(param or "").strip()[:80]
        if kind == "relay":
            try:
                value = validate_url(value)
            except UrlRefused as exc:
                raise RegistryError("invalid relay URL: %s" % exc)
            if param not in ("query", "path"):
                param = "query"
        elif kind == "target":
            try:
                value = validate_url(value)
            except UrlRefused as exc:
                raise RegistryError("invalid target URL: %s" % exc)

        stamp = db.now()
        with self.db.connect() as conn:
            clash = conn.execute(
                "SELECT 1 FROM url_grammar WHERE kind = ? AND value = ? AND param = ?",
                (kind, value, param)).fetchone()
            if clash:
                raise RegistryError("this grammar entry already exists")
            cur = conn.execute(
                "INSERT INTO url_grammar(kind, value, param, enabled, origin, note, created_utc)"
                " VALUES (?,?,?, 1, 'human', ?, ?)",
                (kind, value, param, str(note or "")[:500], stamp))
            gid = cur.lastrowid
        self._event("added grammar %s: %s" % (kind, value[:80]))
        with self.db.connect() as conn:
            return _row(conn.execute("SELECT * FROM url_grammar WHERE id = ?", (gid,)).fetchone())

    def set_grammar_enabled(self, gid, enabled):
        stamp = db.now()
        val = 1 if enabled else 0
        with self.db.connect() as conn:
            conn.execute("UPDATE url_grammar SET enabled = ? WHERE id = ?", (val, gid))
            row = conn.execute("SELECT * FROM url_grammar WHERE id = ?", (gid,)).fetchone()
        if not row:
            raise RegistryError("grammar entry not found")
        self._event("grammar #%d %s" % (gid, "enabled" if val else "disabled"))
        return _row(row)

    def delete_grammar(self, gid):
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM url_grammar WHERE id = ?", (gid,)).fetchone()
            if not row:
                return False
            conn.execute("DELETE FROM url_grammar WHERE id = ?", (gid,))
        self._event("deleted grammar entry: %s" % row["value"][:80])
        return True

    def grammar_bundle(self):
        """Return enabled grammar items grouped for candidate generation."""
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM url_grammar WHERE enabled = 1 ORDER BY id").fetchall()
        patterns, relays, nonce_probes, jq_probes, targets = [], {}, {}, [], []
        for r in rows:
            k = r["kind"]
            val, param = r["value"], r["param"]
            if k == "pattern":
                patterns.append(val)
            elif k == "relay":
                host = urlsplit(val).hostname or val
                relays[host] = (param or "query", val)
            elif k == "nonce_probe":
                nonce_probes.setdefault(param, []).append(val)
            elif k == "jq_probe":
                jq_probes.append(val)
            elif k == "target":
                targets.append(val)
        return {
            "patterns": patterns,
            "relays": relays,
            "nonce_probes": nonce_probes,
            "jq_probes": jq_probes,
            "targets": targets,
        }

    # -- wordlists ----------------------------------------------------------

    def import_wordlist(self, text, iocs, activate=False):
        """Parse wordlist text and propose each term. Returns counts."""
        lines = [line for line in (text or "").splitlines()[:5000]]
        added, skipped, refused = 0, 0, 0
        for term, category in parse_wordlist(lines):
            ioc, reason = iocs.propose(
                term, category=category, provenance="import", actor="human",
                note="imported by operator")
            if ioc is None:
                refused += 1
            elif reason == "created":
                added += 1
                if activate and ioc.get("status") == "proposed":
                    iocs.decide(ioc["id"], "accept", "activated on import")
            else:
                skipped += 1
        self._event("imported wordlist: %d added, %d skipped, %d refused"
                    % (added, skipped, refused))
        return {"added": added, "skipped": skipped, "refused": refused}
