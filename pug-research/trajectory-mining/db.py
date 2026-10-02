"""SQLite index for trajectory mining. Standard library only.

The index carries `INDEX_SCHEMA_VERSION` in its `meta` table.
Version 1 was a guessed layout. Version 2 reads the real dataset fields.
A reader MUST refuse an index with another version. It MUST NOT migrate it silently.
Use a new file name or `importer --rebuild` to start over.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

INDEX_SCHEMA_VERSION = 2
DEFAULT_DB_PATH = Path("../../data/raw/trajectories/index-v2.db")


class IndexVersionError(Exception):
    """Raised when an index file has a missing or different schema version."""


TABLES_DDL = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS checkpoints (
    table_name TEXT PRIMARY KEY,
    status TEXT NOT NULL,            -- complete | partial | missing
    rows_read INTEGER NOT NULL,
    rows_indexed INTEGER NOT NULL,
    rows_skipped INTEGER NOT NULL,
    reasons TEXT NOT NULL,           -- JSON object: reason -> count
    manifest_rows INTEGER,
    seconds REAL NOT NULL,
    completed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shape_counts (
    table_name TEXT NOT NULL,
    shape TEXT NOT NULL,
    supported INTEGER NOT NULL,
    n INTEGER NOT NULL,
    PRIMARY KEY (table_name, shape)
);

CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, model TEXT, line INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY, name TEXT, line INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    scope TEXT NOT NULL,             -- village | agent
    agent_id TEXT,
    label TEXT NOT NULL,
    description TEXT,
    starts_at TEXT,
    ends_at TEXT,                    -- recorded end, may be NULL
    effective_end TEXT,              -- end used for matching (see goals.py)
    source_table TEXT NOT NULL,
    line INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,              -- computer_use | claude_code
    agent_id TEXT,
    sdk_session_id TEXT,
    goal_text TEXT,                  -- stated intention, NULL when absent
    short_goal TEXT,
    started_at TEXT,
    updated_at TEXT,
    first_turn_at TEXT,
    last_turn_at TEXT,
    window_end TEXT,
    item_count INTEGER NOT NULL DEFAULT 0,
    source_table TEXT NOT NULL,
    line INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS turns (
    line INTEGER PRIMARY KEY,
    id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    created_at TEXT,
    action TEXT NOT NULL,
    surface TEXT NOT NULL,
    work TEXT NOT NULL,
    detail TEXT,
    detail_path TEXT,
    output TEXT,
    narration TEXT,
    has_error INTEGER NOT NULL,
    shape TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT NOT NULL,
    source_table TEXT NOT NULL,      -- claude_code_messages | chat_messages
    line INTEGER NOT NULL,
    session_id TEXT,                 -- resolved through sdk_session_id
    session_ref TEXT,                -- raw sdk_session_id
    agent_id TEXT,
    speaker_id TEXT,
    speaker_type TEXT,
    room_id TEXT,
    episode_id TEXT,
    role TEXT,
    created_at TEXT,
    text TEXT,
    text_path TEXT,
    tools TEXT,
    shape TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT NOT NULL,
    line INTEGER NOT NULL,
    event_index INTEGER,
    created_at TEXT,
    action_type TEXT NOT NULL,
    agent_id TEXT,
    session_ref TEXT,
    message_id TEXT,
    room_id TEXT,
    summary TEXT,
    mirrored INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS artifacts (
    owner_id TEXT NOT NULL,          -- session:<id> | episode:<id>
    kind TEXT NOT NULL,              -- url | host | repo | file | document | title
    identifier TEXT NOT NULL,
    scope TEXT NOT NULL,             -- global | agent:<id>
    agent_id TEXT,
    first_at TEXT,
    source_table TEXT NOT NULL,
    source_id TEXT NOT NULL,
    field_path TEXT NOT NULL,
    mentions INTEGER NOT NULL,
    PRIMARY KEY (owner_id, kind, identifier, scope)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    room_name TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT NOT NULL,
    message_count INTEGER NOT NULL,
    agent_count INTEGER NOT NULL,
    first_message_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episode_members (
    episode_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    n_messages INTEGER NOT NULL,
    first_message_id TEXT NOT NULL,
    PRIMARY KEY (episode_id, agent_id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS goal_links (
    owner_id TEXT NOT NULL,          -- session:<id> | episode:<id>
    goal_id TEXT NOT NULL,           -- goal id or unknown_goal
    overlap TEXT NOT NULL,           -- within | crosses_start | crosses_end | spans | none
    agent_id TEXT,
    PRIMARY KEY (owner_id, goal_id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS language_links (
    term TEXT NOT NULL,
    kind TEXT NOT NULL,              -- phrase | term
    owner_id TEXT NOT NULL,
    agent_id TEXT,
    n_owners INTEGER NOT NULL,
    n_agents INTEGER NOT NULL,
    score REAL NOT NULL,
    source_table TEXT NOT NULL,
    source_id TEXT NOT NULL,
    field_path TEXT NOT NULL,
    PRIMARY KEY (term, kind, owner_id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS llm_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    max_usd REAL NOT NULL,
    spent_usd REAL NOT NULL,
    calls INTEGER NOT NULL,
    status TEXT NOT NULL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS llm_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    relation TEXT NOT NULL,
    rationale TEXT NOT NULL,
    cited_ids TEXT NOT NULL,         -- JSON list of ids that were sent to the model
    evidence_class TEXT NOT NULL DEFAULT 'inferred'
);
"""

INDEXES_DDL = {
    "turns": """
        CREATE INDEX IF NOT EXISTS idx_turns_session ON turns (session_id, created_at, line);
        CREATE INDEX IF NOT EXISTS idx_turns_id ON turns (id);
    """,
    "sessions": """
        CREATE INDEX IF NOT EXISTS idx_sessions_agent ON sessions (agent_id, started_at);
        CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions (started_at, window_end);
        CREATE INDEX IF NOT EXISTS idx_sessions_sdk ON sessions (sdk_session_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_list ON sessions (kind, agent_id, started_at, id);
    """,
    "messages": """
        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages (session_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_messages_id ON messages (id);
        CREATE INDEX IF NOT EXISTS idx_messages_episode ON messages (episode_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_messages_room ON messages (room_id, created_at, line);
    """,
    "events": """
        CREATE INDEX IF NOT EXISTS idx_events_order ON events (event_index, created_at, id);
        CREATE INDEX IF NOT EXISTS idx_events_message ON events (message_id);
        CREATE INDEX IF NOT EXISTS idx_events_session ON events (session_ref);
    """,
    "artifacts": """
        CREATE INDEX IF NOT EXISTS idx_artifacts_ident ON artifacts (kind, identifier, scope);
    """,
    "goals": """
        CREATE INDEX IF NOT EXISTS idx_goals_time ON goals (starts_at, effective_end);
    """,
    "goal_links": """
        CREATE INDEX IF NOT EXISTS idx_goal_links_goal ON goal_links (goal_id);
    """,
    "episodes": """
        CREATE INDEX IF NOT EXISTS idx_episodes_time ON episodes (started_at, ended_at);
    """,
    "language_links": """
        CREATE INDEX IF NOT EXISTS idx_language_owner ON language_links (owner_id);
    """,
}

def create_indexes(conn: sqlite3.Connection, *tables: str) -> None:
    for name in tables:
        conn.executescript(INDEXES_DDL[name])


def _read_version(conn: sqlite3.Connection) -> int | None:
    try:
        row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
    except sqlite3.Error:
        return None
    return int(row[0]) if row else None


def connect(path: Path, create: bool = False, readonly: bool = False) -> sqlite3.Connection:
    """Open an index. Raise IndexVersionError when the version does not match."""
    path = Path(path)
    if not path.exists() and not create:
        raise FileNotFoundError("index file not found")
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    if readonly:
        conn = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True, check_same_thread=False)
    else:
        conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    version = _read_version(conn)
    if version is None and create and not readonly:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.executescript(TABLES_DDL)
        conn.execute(
            "INSERT OR REPLACE INTO meta VALUES ('schema_version', ?)", (str(INDEX_SCHEMA_VERSION),)
        )
        conn.commit()
        return conn
    if version != INDEX_SCHEMA_VERSION:
        conn.close()
        raise IndexVersionError(
            f"index schema version {version} does not match {INDEX_SCHEMA_VERSION}; "
            "rebuild with a new --db path or --rebuild"
        )
    if not readonly:
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.executescript(TABLES_DDL)  # adds tables introduced after the build (IF NOT EXISTS)
    return conn
