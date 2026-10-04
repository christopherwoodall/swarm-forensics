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
    for index in range(version, len(MIGRATIONS)):
        conn.executescript("BEGIN;" + MIGRATIONS[index])
        conn.execute("PRAGMA user_version = %d" % (index + 1))
        conn.commit()
    return len(MIGRATIONS)


class Database:
    """Opens short-lived connections to one database file."""

    def __init__(self, path):
        self.path = str(path)
        with self.connect() as conn:
            migrate(conn)

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
