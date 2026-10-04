"""Coverage report for an index build. Counts only, no record values."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

# Checkpoint table -> manifest key. Indexed rows are compared with manifest claims.
MANIFEST_KEYS = (
    "agents", "chat_rooms", "village_goals", "agent_goals", "computer_use_sessions",
    "claude_code_sessions", "computer_use_turns", "claude_code_messages", "chat_messages",
    "events", "agent_memories",
)  # fmt: skip


def _one(conn: sqlite3.Connection, sql: str, *args: Any) -> int:
    row = conn.execute(sql, args).fetchone()
    return int(row[0] or 0)


def coverage_report(
    conn: sqlite3.Connection, db_path: Path, manifest: dict[str, int] | None = None
) -> dict[str, Any]:
    manifest = manifest or {}
    tables: dict[str, Any] = {}
    for row in conn.execute("SELECT * FROM checkpoints ORDER BY table_name"):
        claim = row["manifest_rows"] if row["manifest_rows"] is not None else manifest.get(
            row["table_name"]
        )
        entry = {
            "status": row["status"],
            "rows_read": row["rows_read"],
            "rows_indexed": row["rows_indexed"],
            "rows_skipped": row["rows_skipped"],
            "reasons": json.loads(row["reasons"]),
            "manifest_rows": claim,
            "seconds": row["seconds"],
        }
        if claim is not None and not row["table_name"].startswith("derived:"):
            entry["manifest_gap"] = claim - row["rows_read"]
        tables[row["table_name"]] = entry
    missing = [k for k in MANIFEST_KEYS if k in manifest and k not in tables]

    unsupported = [
        {"table": r["table_name"], "shape": r["shape"], "rows": r["n"]}
        for r in conn.execute(
            "SELECT table_name, shape, n FROM shape_counts WHERE supported = 0 ORDER BY n DESC"
        )
    ]
    shapes: dict[str, dict[str, int]] = {}
    for r in conn.execute(
        "SELECT table_name, shape, n FROM shape_counts WHERE supported = 1 "
        "AND shape NOT LIKE 'actionType:%' ORDER BY table_name, shape"
    ):
        shapes.setdefault(r["table_name"], {})[r["shape"]] = r["n"]

    orphans = {
        "turns_without_session": _one(
            conn,
            "SELECT COUNT(*) FROM turns t WHERE NOT EXISTS "
            "(SELECT 1 FROM sessions s WHERE s.id = t.session_id)",
        ),
        "sessions_without_agent": _one(
            conn,
            "SELECT COUNT(*) FROM sessions s WHERE s.agent_id IS NULL OR NOT EXISTS "
            "(SELECT 1 FROM agents a WHERE a.id = s.agent_id)",
        ),
        "messages_without_session": _one(
            conn,
            "SELECT COUNT(*) FROM messages WHERE source_table = 'claude_code_messages' "
            "AND session_id IS NULL",
        ),
        "computer_use_sessions_without_turns": _one(
            conn,
            "SELECT COUNT(*) FROM sessions WHERE kind = 'computer_use' AND item_count = 0",
        ),
        "claude_code_sessions_without_messages": _one(
            conn,
            "SELECT COUNT(*) FROM sessions WHERE kind = 'claude_code' AND item_count = 0",
        ),
        "computer_use_sessions_without_session_goal": _one(
            conn,
            "SELECT COUNT(*) FROM sessions WHERE kind = 'computer_use' AND goal_text IS NULL",
        ),
        "sessions_with_unknown_goal_context": _one(
            conn,
            "SELECT COUNT(*) FROM goal_links WHERE goal_id = 'unknown_goal' "
            "AND owner_id LIKE 'session:%'",
        ),
        "chat_messages_without_room": _one(
            conn,
            "SELECT COUNT(*) FROM messages WHERE source_table = 'chat_messages' "
            "AND room_id IS NULL",
        ),
    }
    agent_goal_agents = _one(conn, "SELECT COUNT(DISTINCT agent_id) FROM goals WHERE scope='agent'")
    agents = _one(conn, "SELECT COUNT(*) FROM agents")
    chat = {
        "chat_messages": _one(
            conn, "SELECT COUNT(*) FROM messages WHERE source_table = 'chat_messages'"
        ),
        "duplicate_chat_message_ids": _one(
            conn,
            "SELECT COUNT(*) - COUNT(DISTINCT id) FROM messages "
            "WHERE source_table = 'chat_messages'",
        ),
        "talk_events_mirrored_in_chat": _one(conn, "SELECT COUNT(*) FROM events WHERE mirrored = 1"),
        "talk_events_without_chat_row": _one(
            conn, "SELECT COUNT(*) FROM events WHERE message_id IS NOT NULL AND mirrored = 0"
        ),
        "episodes": _one(conn, "SELECT COUNT(*) FROM episodes"),
    }
    size = sum(
        Path(str(db_path) + s).stat().st_size
        for s in ("", "-wal")
        if Path(str(db_path) + s).exists()
    )
    meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta")}
    return {
        "schema_version": int(meta.get("schema_version", 0)),
        "sample_limit": meta.get("limit") or None,
        "tables": tables,
        "manifest_tables_not_read": missing,
        "unsupported_shapes": unsupported,
        "supported_shapes": shapes,
        "orphans_and_gaps": orphans,
        "agents": {"agents": agents, "agents_with_agent_goal_rows": agent_goal_agents},
        "chat": chat,
        "storage": {"db_bytes_with_wal": size, "db_mb": round(size / (1 << 20), 1)},
        "total_import_seconds": round(
            sum(t["seconds"] for k, t in tables.items() if not k.startswith("derived:")), 1
        ),
    }
