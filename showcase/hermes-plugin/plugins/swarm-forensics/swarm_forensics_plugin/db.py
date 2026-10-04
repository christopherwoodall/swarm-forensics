"""SQLite storage: connection, versioned migrations, shared helpers.

The database is the source of truth for hunts, evidence, IOCs, and the
entity graph. WAL mode lets the worker thread and the API read and write
at once. Every connection is short-lived and owned by one thread. All SQL
MUST be parameterized.
"""

import contextlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Each entry upgrades the schema by one version. Append only.
MIGRATIONS = [
    """
    CREATE TABLE settings(
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    );
    CREATE TABLE hunts(
        id TEXT PRIMARY KEY,
        origin TEXT NOT NULL,
        goal TEXT NOT NULL,
        state TEXT NOT NULL,
        detail TEXT NOT NULL DEFAULT '',
        created_utc TEXT NOT NULL,
        started_utc TEXT,
        ended_utc TEXT,
        cycle INTEGER NOT NULL DEFAULT 0,
        owner TEXT,
        heartbeat_utc TEXT,
        stop_requested INTEGER NOT NULL DEFAULT 0,
        pause_requested INTEGER NOT NULL DEFAULT 0,
        stats TEXT NOT NULL DEFAULT '{}',
        max_cycles INTEGER NOT NULL DEFAULT 0,
        schedule_id TEXT
    );
    CREATE TABLE events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hunt_id TEXT,
        ts TEXT NOT NULL,
        kind TEXT NOT NULL,
        level TEXT NOT NULL DEFAULT 'info',
        message TEXT NOT NULL,
        data TEXT NOT NULL DEFAULT '{}'
    );
    CREATE INDEX idx_events_hunt ON events(hunt_id, id);
    CREATE TABLE queries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hunt_id TEXT,
        source TEXT NOT NULL,
        query TEXT NOT NULL,
        outcome TEXT NOT NULL,
        http_status INTEGER NOT NULL DEFAULT 0,
        result_count INTEGER NOT NULL DEFAULT 0,
        ts TEXT NOT NULL
    );
    CREATE INDEX idx_queries_lookup ON queries(source, query);
    CREATE TABLE evidence(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hunt_id TEXT,
        source TEXT NOT NULL,
        query TEXT NOT NULL DEFAULT '',
        url TEXT NOT NULL,
        title TEXT NOT NULL DEFAULT '',
        excerpt TEXT NOT NULL DEFAULT '',
        content_hash TEXT NOT NULL,
        observed_utc TEXT NOT NULL,
        claim_level TEXT NOT NULL DEFAULT 'L1',
        tainted INTEGER NOT NULL DEFAULT 0,
        analysis TEXT NOT NULL DEFAULT '{}',
        UNIQUE(url, content_hash)
    );
    CREATE TABLE iocs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT NOT NULL UNIQUE COLLATE NOCASE,
        category TEXT NOT NULL DEFAULT 'proposed',
        status TEXT NOT NULL
            CHECK(status IN ('proposed','active','inactive','rejected')),
        origin TEXT NOT NULL,
        confidence REAL NOT NULL DEFAULT 0,
        provenance TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT '',
        added_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    );
    CREATE INDEX idx_iocs_status ON iocs(status);
    CREATE TABLE ioc_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ioc_id INTEGER NOT NULL REFERENCES iocs(id) ON DELETE CASCADE,
        ts TEXT NOT NULL,
        from_status TEXT,
        to_status TEXT NOT NULL,
        actor TEXT NOT NULL,
        reason TEXT NOT NULL DEFAULT ''
    );
    CREATE TABLE ioc_evidence(
        ioc_id INTEGER NOT NULL REFERENCES iocs(id) ON DELETE CASCADE,
        evidence_id INTEGER NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
        PRIMARY KEY(ioc_id, evidence_id)
    );
    CREATE TABLE entities(
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL
            CHECK(type IN ('agent','swarm','case','trace','collection')),
        name TEXT NOT NULL COLLATE NOCASE,
        summary TEXT NOT NULL DEFAULT '',
        notes TEXT NOT NULL DEFAULT '',
        attrs TEXT NOT NULL DEFAULT '{}',
        origin TEXT NOT NULL DEFAULT 'human',
        created_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL,
        UNIQUE(type, name)
    );
    CREATE TABLE links(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        src TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
        dst TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
        kind TEXT NOT NULL,
        evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
        created_utc TEXT NOT NULL,
        UNIQUE(src, dst, kind)
    );
    CREATE INDEX idx_links_dst ON links(dst);
    CREATE TABLE indicators(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
        kind TEXT NOT NULL,
        value TEXT NOT NULL,
        evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
        first_seen_utc TEXT NOT NULL,
        UNIQUE(entity_id, kind, value)
    );
    CREATE TABLE entity_evidence(
        entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
        evidence_id INTEGER NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
        PRIMARY KEY(entity_id, evidence_id)
    );
    CREATE TABLE leads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hunt_id TEXT,
        kind TEXT NOT NULL,
        value TEXT NOT NULL,
        priority REAL NOT NULL DEFAULT 0.5,
        status TEXT NOT NULL DEFAULT 'open',
        origin TEXT NOT NULL DEFAULT 'model',
        created_utc TEXT NOT NULL,
        UNIQUE(kind, value)
    );
    CREATE TABLE cursors(
        source TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        PRIMARY KEY(source, key)
    );
    CREATE TABLE candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        template TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'unprobed',
        hits INTEGER NOT NULL DEFAULT 0,
        created_utc TEXT NOT NULL,
        probed_utc TEXT
    );
    CREATE TABLE schedules(
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        kind TEXT NOT NULL CHECK(kind IN ('interval','cron')),
        spec TEXT NOT NULL,
        goal TEXT NOT NULL,
        max_cycles INTEGER NOT NULL DEFAULT 5,
        enabled INTEGER NOT NULL DEFAULT 0,
        armed_utc TEXT,
        last_run_utc TEXT,
        next_run_utc TEXT
    );
    """,
    # Migration 2: hierarchy types, `part_of` links, editable registries.
    # `entities` is rebuilt because SQLite cannot alter a CHECK constraint.
    """
    CREATE TABLE entities_v2(
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL
            CHECK(type IN ('artifact','agent','swarm','campaign','collection')),
        name TEXT NOT NULL COLLATE NOCASE,
        summary TEXT NOT NULL DEFAULT '',
        notes TEXT NOT NULL DEFAULT '',
        attrs TEXT NOT NULL DEFAULT '{}',
        origin TEXT NOT NULL DEFAULT 'human',
        created_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL,
        UNIQUE(type, name)
    );
    INSERT INTO entities_v2
        SELECT id,
               CASE type WHEN 'trace' THEN 'artifact'
                         WHEN 'case' THEN 'campaign' ELSE type END,
               name, summary, notes, attrs, origin, created_utc, updated_utc
        FROM entities;
    DROP TABLE entities;
    ALTER TABLE entities_v2 RENAME TO entities;
    UPDATE OR IGNORE links SET kind = 'part_of'
        WHERE kind IN ('member_of','trace_of');
    DELETE FROM links WHERE kind IN ('member_of','trace_of');
    CREATE TABLE index_sources(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        kind TEXT NOT NULL CHECK(kind IN ('cdx','urlquery')),
        endpoint TEXT NOT NULL,
        config TEXT NOT NULL DEFAULT '{}',
        enabled INTEGER NOT NULL DEFAULT 0,
        probe_candidates INTEGER NOT NULL DEFAULT 0,
        origin TEXT NOT NULL DEFAULT 'human',
        note TEXT NOT NULL DEFAULT '',
        created_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    );
    CREATE TABLE url_grammar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kind TEXT NOT NULL
            CHECK(kind IN ('pattern','relay','nonce_probe','jq_probe','target')),
        value TEXT NOT NULL,
        param TEXT NOT NULL DEFAULT '',
        enabled INTEGER NOT NULL DEFAULT 1,
        origin TEXT NOT NULL DEFAULT 'human',
        note TEXT NOT NULL DEFAULT '',
        created_utc TEXT NOT NULL,
        UNIQUE(kind, value, param)
    );
    """,
    # Migration 3: DB prompts, URL catalog & benign status, entity tags.
    """
    CREATE TABLE prompts(
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        template TEXT NOT NULL,
        default_template TEXT NOT NULL,
        variables TEXT NOT NULL DEFAULT '[]',
        updated_utc TEXT NOT NULL
    );
    CREATE TABLE urls(
        url TEXT PRIMARY KEY,
        host TEXT NOT NULL,
        source TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'discovered'
            CHECK(status IN ('discovered','examined','benign','suspicious')),
        reason TEXT NOT NULL DEFAULT '',
        discovered_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    );
    CREATE INDEX idx_urls_status ON urls(status);
    CREATE INDEX idx_urls_host ON urls(host);
    ALTER TABLE entities ADD COLUMN tags TEXT NOT NULL DEFAULT '[]';
    CREATE TABLE iocs_v3(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT NOT NULL UNIQUE COLLATE NOCASE,
        category TEXT NOT NULL DEFAULT 'proposed',
        status TEXT NOT NULL
            CHECK(status IN ('proposed','active','inactive','rejected','benign')),
        origin TEXT NOT NULL,
        confidence REAL NOT NULL DEFAULT 0,
        provenance TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT '',
        added_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    );
    INSERT INTO iocs_v3
        SELECT id, term, category, status, origin, confidence, provenance, note,
               added_utc, updated_utc
        FROM iocs;
    DROP TABLE iocs;
    ALTER TABLE iocs_v3 RENAME TO iocs;
    CREATE INDEX idx_iocs_status ON iocs(status);
    """,
    # Migration 4: recursive sub-hunts (parent_hunt_id, depth, session_id).
    """
    ALTER TABLE hunts ADD COLUMN parent_hunt_id TEXT REFERENCES hunts(id) ON DELETE SET NULL;
    ALTER TABLE hunts ADD COLUMN depth INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE hunts ADD COLUMN session_id TEXT;
    CREATE INDEX idx_hunts_parent ON hunts(parent_hunt_id);
    CREATE INDEX idx_hunts_session ON hunts(session_id);
    """,
    # Migration 5: session bindings, corpus observations, and local text mirrors.
    """
    CREATE TABLE IF NOT EXISTS session_bindings(
        session_id TEXT PRIMARY KEY,
        session_key TEXT,
        hunt_id TEXT NOT NULL,
        bound_utc TEXT NOT NULL,
        FOREIGN KEY(hunt_id) REFERENCES hunts(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_bindings_hunt ON session_bindings(hunt_id);

    CREATE TABLE IF NOT EXISTS corpus_observations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hunt_id TEXT,
        session_id TEXT,
        tool_name TEXT NOT NULL,
        query_or_url TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'observed',
        result_summary TEXT NOT NULL DEFAULT '',
        sha256 TEXT NOT NULL DEFAULT '',
        observed_utc TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_obs_hunt ON corpus_observations(hunt_id);
    CREATE INDEX IF NOT EXISTS idx_obs_session ON corpus_observations(session_id);

    CREATE TABLE IF NOT EXISTS mirrors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        sha256 TEXT NOT NULL,
        path TEXT NOT NULL,
        byte_count INTEGER NOT NULL DEFAULT 0,
        tainted INTEGER NOT NULL DEFAULT 0,
        hunt_id TEXT,
        session_id TEXT,
        fetched_utc TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_mirrors_sha ON mirrors(sha256);
    CREATE INDEX IF NOT EXISTS idx_mirrors_hunt ON mirrors(hunt_id);
    """,
    # Migration 6: preserve morphology candidates without replacing session storage.
    """
    CREATE TABLE morphology_candidates(
        id TEXT PRIMARY KEY,
        candidate_id TEXT NOT NULL UNIQUE,
        candidate_label TEXT NOT NULL,
        candidate_status TEXT NOT NULL CHECK(candidate_status IN (
            'known_variant','possible_new_morphology','anomaly','weak_lead')),
        evidence_strength TEXT NOT NULL CHECK(evidence_strength IN (
            'e0','e1','e2','e3','e4','e5')),
        card_json TEXT NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'new' CHECK(review_status IN (
            'new','investigating','resolved','dismissed')),
        review_reason TEXT NOT NULL DEFAULT '',
        tainted INTEGER NOT NULL DEFAULT 0 CHECK(tainted IN (0,1)),
        created_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    );
    CREATE INDEX idx_morphology_review ON morphology_candidates(review_status, created_utc);
    CREATE TABLE morphology_candidate_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_record_id TEXT NOT NULL REFERENCES morphology_candidates(id) ON DELETE CASCADE,
        ts TEXT NOT NULL,
        from_status TEXT,
        to_status TEXT NOT NULL CHECK(to_status IN (
            'new','investigating','resolved','dismissed')),
        actor TEXT NOT NULL,
        reason TEXT NOT NULL DEFAULT ''
    );
    CREATE INDEX idx_morphology_log ON morphology_candidate_log(candidate_record_id, id);
    """,
]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id():
    return uuid.uuid4().hex[:16]


def dumps(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def loads(text, default=None):
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return default


def migrate(conn):
    """Apply pending migrations. Idempotent. Returns the schema version."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version >= len(MIGRATIONS):
        return len(MIGRATIONS)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        for index in range(version, len(MIGRATIONS)):
            conn.executescript("BEGIN;" + MIGRATIONS[index])
            violations = conn.execute("PRAGMA foreign_key_check").fetchall()
            if violations:
                conn.rollback()
                raise RuntimeError("Foreign key check failed after migration %d: %s"
                                   % (index + 1, violations))
            conn.execute("PRAGMA user_version = %d" % (index + 1))
            conn.commit()
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
    return len(MIGRATIONS)


class Database:
    """Opens short-lived connections to one database file."""

    def __init__(self, path):
        self.path = str(path)
        self._maybe_backup()
        with self.connect() as conn:
            migrate(conn)

    def _maybe_backup(self):
        p = Path(self.path)
        if not p.is_file() or str(self.path) == ":memory:":
            return
        try:
            temp_conn = sqlite3.connect(self.path)
            ver = temp_conn.execute("PRAGMA user_version").fetchone()[0]
            if ver < len(MIGRATIONS):
                bak = p.with_name("%s.v%d.bak" % (p.name, ver))
                if not bak.exists():
                    dest = sqlite3.connect(str(bak))
                    temp_conn.backup(dest)
                    dest.close()
            temp_conn.close()
        except Exception:
            pass

    @contextlib.contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 30000")
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def reset(self):
        """Wipe all tables and re-apply all migrations from scratch."""
        with self.connect() as conn:
            conn.execute("PRAGMA foreign_keys = OFF")
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
            for r in rows:
                conn.execute("DROP TABLE IF EXISTS %s" % r["name"])
            conn.execute("PRAGMA user_version = 0")
            migrate(conn)
