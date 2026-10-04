"""Goal windows and temporal context links.

Rules (documented):
- A goal covers `[starts_at, effective_end]`. Both bounds are inclusive.
- A goal with a recorded end uses it. A goal without one ends when the next goal in the same
  group starts. Groups are `village` and one group per agent. The last goal stays open.
- A goal without `starts_at` cannot be placed. It never links.
- Village goals apply to every agent. An agent goal applies to its own agent only.
- A session window is `[started_at, window_end]`. Chat episodes use their own first and last time.
- Overlapping goals all link. A trace that crosses a boundary links to both sides.
- A trace with no matching goal links to `unknown_goal`. It is never dropped.
A link says the trace happened inside the goal window. It never says the trace worked on the goal.
"""

from __future__ import annotations

import sqlite3

UNKNOWN_GOAL = "unknown_goal"
OPEN_END = "9999-12-31 00:00:00.000000"
TEMPORAL_LABEL = "temporal_context"


def overlap_kind(ws: str, we: str, gs: str, ge: str | None) -> str:
    """Classify how a trace window [ws, we] meets a goal window [gs, ge]."""
    ge = ge or OPEN_END
    if ws > ge or we < gs:
        return "none"
    if ws >= gs and we <= ge:
        return "within"
    if ws < gs and we <= ge:
        return "crosses_start"
    if ws >= gs and we > ge:
        return "crosses_end"
    return "spans"


def resolve_windows(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT id, scope, agent_id, starts_at, ends_at FROM goals ORDER BY starts_at, id"
    ).fetchall()
    groups: dict[str, list[tuple]] = {}
    unplaced = 0
    for gid, scope, agent, start, end in rows:
        if not start:
            unplaced += 1
            continue
        group = "village" if scope == "village" else f"agent:{agent}"
        groups.setdefault(group, []).append((gid, start, end))
    updates = []
    for items in groups.values():
        for i, (gid, start, end) in enumerate(items):
            effective = end
            if not effective:
                later = [s for _g, s, _e in items[i + 1 :] if s > start]
                effective = later[0] if later else None
            updates.append((effective, gid))
    with conn:
        conn.execute("UPDATE goals SET effective_end = NULL")
        conn.executemany("UPDATE goals SET effective_end = ? WHERE id = ?", updates)
    return {"goals_placed": len(updates), "goals_without_start": unplaced}


_CASE = f"""
CASE
  WHEN ws > COALESCE(g.effective_end, '{OPEN_END}') OR we < g.starts_at THEN 'none'
  WHEN ws >= g.starts_at AND we <= COALESCE(g.effective_end, '{OPEN_END}') THEN 'within'
  WHEN ws < g.starts_at AND we <= COALESCE(g.effective_end, '{OPEN_END}') THEN 'crosses_start'
  WHEN ws >= g.starts_at AND we > COALESCE(g.effective_end, '{OPEN_END}') THEN 'crosses_end'
  ELSE 'spans'
END
"""


def build_goal_links(conn: sqlite3.Connection) -> dict[str, int]:
    stats = resolve_windows(conn)
    with conn:
        conn.execute("DELETE FROM goal_links")
        conn.execute(
            f"""
            INSERT OR REPLACE INTO goal_links
            SELECT owner_id, goal_id, overlap, agent_id FROM (
                SELECT 'session:' || s.id AS owner_id, g.id AS goal_id, s.agent_id AS agent_id,
                       {_CASE} AS overlap
                FROM (SELECT id, agent_id, started_at AS ws,
                             COALESCE(window_end, started_at) AS we FROM sessions
                      WHERE started_at IS NOT NULL) s
                JOIN goals g ON g.starts_at IS NOT NULL
                             AND (g.scope = 'village' OR g.agent_id = s.agent_id)
            ) WHERE overlap != 'none'
            """
        )
        conn.execute(
            f"""
            INSERT OR REPLACE INTO goal_links
            SELECT owner_id, goal_id, overlap, NULL FROM (
                SELECT 'episode:' || e.id AS owner_id, g.id AS goal_id,
                       {_CASE} AS overlap
                FROM (SELECT id, started_at AS ws, ended_at AS we FROM episodes) e
                JOIN goals g ON g.starts_at IS NOT NULL AND g.scope = 'village'
            ) WHERE overlap != 'none'
            """
        )
        conn.execute(
            f"""
            INSERT OR IGNORE INTO goal_links
            SELECT 'session:' || s.id, '{UNKNOWN_GOAL}', 'none', s.agent_id FROM sessions s
            WHERE NOT EXISTS (SELECT 1 FROM goal_links l WHERE l.owner_id = 'session:' || s.id)
            """
        )
        conn.execute(
            f"""
            INSERT OR IGNORE INTO goal_links
            SELECT 'episode:' || e.id, '{UNKNOWN_GOAL}', 'none', NULL FROM episodes e
            WHERE NOT EXISTS (SELECT 1 FROM goal_links l WHERE l.owner_id = 'episode:' || e.id)
            """
        )
    stats["links"] = conn.execute("SELECT COUNT(*) FROM goal_links").fetchone()[0]
    stats["unknown_goal_links"] = conn.execute(
        "SELECT COUNT(*) FROM goal_links WHERE goal_id = ?", (UNKNOWN_GOAL,)
    ).fetchone()[0]
    stats["boundary_crossing"] = conn.execute(
        "SELECT COUNT(DISTINCT owner_id) FROM goal_links "
        "WHERE overlap IN ('crosses_start', 'crosses_end', 'spans')"
    ).fetchone()[0]
    return stats
