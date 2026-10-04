"""Chat episodes: consecutive messages in one room, split by a silence gap.

Rule (documented, deterministic): order each room by (created_at, line).
Start a new episode when the gap to the previous message exceeds `EPISODE_GAP_MINUTES`.
An episode lists who spoke. It does not show who answered whom.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from extract import extract_artifacts

EPISODE_GAP_MINUTES = 30
_FMT = "%Y-%m-%d %H:%M:%S.%f"


def _minutes(a: str, b: str) -> float:
    return (datetime.strptime(b, _FMT) - datetime.strptime(a, _FMT)).total_seconds() / 60


def build_episodes(conn: sqlite3.Connection) -> dict[str, int]:
    with conn:
        conn.execute("DELETE FROM episodes")
        conn.execute("DELETE FROM episode_members")
        conn.execute("DELETE FROM artifacts WHERE owner_id LIKE 'episode:%'")
        conn.execute("UPDATE messages SET episode_id = NULL")
    rooms = {r[0]: r[1] for r in conn.execute("SELECT id, name FROM rooms")}
    cur = conn.execute(
        "SELECT rowid, id, room_id, agent_id, speaker_id, created_at, text FROM messages "
        "WHERE source_table = 'chat_messages' ORDER BY room_id, created_at, line"
    )
    stats = {"episodes": 0, "messages_in_episodes": 0, "messages_without_room_or_time": 0}
    state: dict | None = None
    updates: list[tuple[str, int]] = []

    def close(ep: dict) -> None:
        stats["episodes"] += 1
        stats["messages_in_episodes"] += ep["count"]
        eid = ep["id"]
        conn.execute(
            "INSERT INTO episodes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (eid, ep["room"], rooms.get(ep["room"]), ep["start"], ep["end"], ep["count"],
             len(ep["members"]), ep["first"]),
        )  # fmt: skip
        conn.executemany(
            "INSERT INTO episode_members VALUES (?, ?, ?, ?)",
            [(eid, m, v[0], v[1]) for m, v in sorted(ep["members"].items())],
        )
        updates.extend((eid, rid) for rid in ep["rowids"])
        conn.executemany(
            "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?, 'chat_messages', ?, 'content', ?)",
            [
                (f"episode:{eid}", k, i, sc, a, w, src, n)
                for (k, i, sc), (w, src, a, n) in sorted(ep["artifacts"].items())
            ],
        )

    for rowid, mid, room, agent, speaker, when, text in cur:
        if not room or not when:
            stats["messages_without_room_or_time"] += 1
            continue
        new = (
            state is None
            or state["room"] != room
            or _minutes(state["end"], when) > EPISODE_GAP_MINUTES
        )
        if new:
            if state:
                close(state)
            seq = (state["seq"] + 1) if state and state["room"] == room else 1
            state = {
                "id": f"{room}:{seq:04d}", "seq": seq, "room": room, "start": when, "end": when,
                "count": 0, "first": mid, "members": {}, "rowids": [], "artifacts": {},
            }  # fmt: skip
        assert state is not None
        state["end"] = when
        state["count"] += 1
        state["rowids"].append(rowid)
        member = agent or (f"user:{speaker}" if speaker else "unknown")
        slot = state["members"].setdefault(member, [0, mid])
        slot[0] += 1
        if text:
            for kind, ident, scope in extract_artifacts(text, agent):
                state["artifacts"].setdefault((kind, ident, scope), [when, mid, agent, 0])[3] += 1
    if state:
        close(state)
    cur.close()
    for start in range(0, len(updates), 5000):
        conn.executemany(
            "UPDATE messages SET episode_id = ? WHERE rowid = ?", updates[start : start + 5000]
        )
    conn.commit()
    return stats
