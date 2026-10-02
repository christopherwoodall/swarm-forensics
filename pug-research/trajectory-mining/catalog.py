"""Trace catalog and bounded graph slices for the 3D viewer.

Tiers, top to bottom: agents, actions or episodes, artifacts and messages, stated goals.
Every request reads a bounded slice with indexed SQL. Large traces are aggregated and the
payload says what was hidden. Goal tier nodes show stated intention or temporal context only.
"""

from __future__ import annotations

import math
import re
import sqlite3
from typing import Any

from contract import (
    SCHEMA_VERSION,
    GraphEdge,
    GraphNode,
    SourceRef,
    sanitize_text,
    validate_trajectory_payload,
)
from goals import TEMPORAL_LABEL, UNKNOWN_GOAL

MAX_TRACES = 12
DEFAULT_MAX_NODES = 400
HARD_MAX_NODES = 1500
MAX_ACTIONS_PER_TRACE = 40
MAX_FETCH_ITEMS = 200_000
ARTIFACTS_PER_TRACE = 12
LANGUAGE_PER_TRACE = 8
MESSAGES_PER_EPISODE = 6
MAX_STEPS_PAGE = 200
TRACE_TYPES = ("computer_use", "claude_code", "chat")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHARED_NOTE = (
    "The same identifier appears in more than one trace. "
    "This does not show coordination or who created it."
)
LANGUAGE_NOTE = "Shared wording. It does not show collaboration."
TEMPORAL_NOTE = "The trace window overlaps the goal window. It does not show work on the goal."


class CatalogError(ValueError):
    """Bad request parameter. The message never holds user text."""


def _date_bound(value: str | None, end: bool) -> str | None:
    if not value:
        return None
    if not _DATE.match(value):
        raise CatalogError("date must be YYYY-MM-DD")
    return f"{value} 23:59:59.999999" if end else f"{value} 00:00:00"


def _marks(values: list[Any]) -> str:
    return ",".join("?" * len(values))


def _short(text: str | None, n: int = 70) -> str:
    line = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    return line[:n]


def bucket_plan(n: int, cap: int = MAX_ACTIONS_PER_TRACE) -> tuple[int, int]:
    """Return (bucket size, node count). Size 1 means one node per item."""
    if n <= cap:
        return 1, n
    size = math.ceil(n / cap)
    return size, math.ceil(n / size)


def actions_budget(n_traces: int, max_nodes: int) -> int:
    return max(6, min(MAX_ACTIONS_PER_TRACE, (max_nodes // 2) // max(n_traces, 1)))


class TraceCatalog:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---- catalog -------------------------------------------------------------------------
    def overview(self) -> dict[str, Any]:
        c = self.conn
        agents = [
            dict(r) for r in c.execute(
                "SELECT a.id, a.name, a.model, "
                "(SELECT COUNT(*) FROM sessions s WHERE s.agent_id = a.id "
                " AND s.kind = 'computer_use') AS computer_use, "
                "(SELECT COUNT(*) FROM sessions s WHERE s.agent_id = a.id "
                " AND s.kind = 'claude_code') AS claude_code "
                "FROM agents a ORDER BY a.name COLLATE NOCASE, a.id"
            )
        ]  # fmt: skip
        goals = [
            dict(r) for r in c.execute(
                "SELECT g.id, g.scope, g.agent_id, g.label, g.starts_at, g.effective_end, "
                "(SELECT COUNT(*) FROM goal_links l WHERE l.goal_id = g.id) AS traces "
                "FROM goals g ORDER BY g.starts_at, g.id"
            )
        ]  # fmt: skip
        goals.append(
            {
                "id": UNKNOWN_GOAL, "scope": "none", "agent_id": None,
                "label": "unknown goal (no goal window)", "starts_at": None, "effective_end": None,
                "traces": c.execute(
                    "SELECT COUNT(*) FROM goal_links WHERE goal_id = ?", (UNKNOWN_GOAL,)
                ).fetchone()[0],
            }
        )  # fmt: skip
        lo, hi = c.execute("SELECT MIN(started_at), MAX(started_at) FROM sessions").fetchone()
        meta = {r["key"]: r["value"] for r in c.execute("SELECT key, value FROM meta")}
        counts = {
            "computer_use": c.execute(
                "SELECT COUNT(*) FROM sessions WHERE kind = 'computer_use'"
            ).fetchone()[0],
            "claude_code": c.execute(
                "SELECT COUNT(*) FROM sessions WHERE kind = 'claude_code'"
            ).fetchone()[0],
            "chat": c.execute("SELECT COUNT(*) FROM episodes").fetchone()[0],
        }
        return {
            "agents": agents, "goals": goals, "trace_types": counts,
            "date_range": [lo[:10] if lo else None, hi[:10] if hi else None],
            "index": {"schema_version": int(meta.get("schema_version", 0)),
                      "sample_limit": meta.get("limit") or None,
                      "imported_at": meta.get("imported_at")},
            "limits": {"max_traces": MAX_TRACES, "max_nodes": HARD_MAX_NODES},
        }  # fmt: skip

    def search_traces(
        self,
        agent_ids: list[str] | None = None,
        goal_id: str | None = None,
        types: list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        q: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        types = [t for t in (types or TRACE_TYPES) if t in TRACE_TYPES]
        if not types:
            raise CatalogError("unknown trace type")
        limit = max(1, min(int(limit), 200))
        offset = max(0, int(offset))
        lo, hi = _date_bound(date_from, False), _date_bound(date_to, True)
        parts: list[str] = []
        params: list[Any] = []
        kinds = [t for t in types if t != "chat"]
        if kinds:
            where, p = [f"s.kind IN ({_marks(kinds)})"], list(kinds)
            if agent_ids:
                where.append(f"s.agent_id IN ({_marks(agent_ids)})")
                p += agent_ids
            if goal_id:
                where.append(
                    "EXISTS (SELECT 1 FROM goal_links l WHERE l.owner_id = 'session:' || s.id "
                    "AND l.goal_id = ?)"
                )
                p.append(goal_id)
            if lo:
                where.append("s.started_at >= ?")
                p.append(lo)
            if hi:
                where.append("s.started_at <= ?")
                p.append(hi)
            if q:
                where.append("(s.goal_text LIKE ? OR s.short_goal LIKE ?)")
                p += [f"%{q}%"] * 2
            parts.append(
                "SELECT 'session:' || s.id AS trace_id, s.kind AS type, s.agent_id AS agent_id, "
                "s.started_at AS started_at, COALESCE(s.window_end, s.started_at) AS ended_at, "
                "s.item_count AS items, COALESCE(s.short_goal, s.goal_text) AS label, "
                "(s.goal_text IS NOT NULL) AS has_goal FROM sessions s WHERE "
                + " AND ".join(where)
            )
            params += p
        if "chat" in types:
            where, p = ["1 = 1"], []
            if agent_ids:
                where.append(
                    "EXISTS (SELECT 1 FROM episode_members m WHERE m.episode_id = e.id "
                    f"AND m.agent_id IN ({_marks(agent_ids)}))"
                )
                p += agent_ids
            if goal_id:
                where.append(
                    "EXISTS (SELECT 1 FROM goal_links l WHERE l.owner_id = 'episode:' || e.id "
                    "AND l.goal_id = ?)"
                )
                p.append(goal_id)
            if lo:
                where.append("e.started_at >= ?")
                p.append(lo)
            if hi:
                where.append("e.started_at <= ?")
                p.append(hi)
            if q:
                where.append("e.room_name LIKE ?")
                p.append(f"%{q}%")
            parts.append(
                "SELECT 'episode:' || e.id AS trace_id, 'chat' AS type, NULL AS agent_id, "
                "e.started_at AS started_at, e.ended_at AS ended_at, "
                "e.message_count AS items, COALESCE(e.room_name, e.room_id) AS label, "
                "0 AS has_goal FROM episodes e WHERE "
                + " AND ".join(where)
            )
            params += p
        union = " UNION ALL ".join(parts)
        total = self.conn.execute(f"SELECT COUNT(*) FROM ({union})", params).fetchone()[0]
        rows = self.conn.execute(
            f"SELECT * FROM ({union}) ORDER BY started_at DESC, trace_id LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()
        names = {r[0]: r[1] for r in self.conn.execute("SELECT id, name FROM agents")}
        traces = []
        for r in rows:
            item = dict(r)
            if item["type"] == "chat":
                eid = item["trace_id"].split(":", 1)[1]
                members = [
                    m[0] for m in self.conn.execute(
                        "SELECT agent_id FROM episode_members WHERE episode_id = ? "
                        "ORDER BY n_messages DESC, agent_id LIMIT 8", (eid,)
                    )
                ]  # fmt: skip
                item["agent_ids"] = members
            else:
                item["agent_ids"] = [item["agent_id"]] if item["agent_id"] else []
            item["agent_names"] = [names.get(a, a) for a in item["agent_ids"]]
            item["label"] = _short(item["label"]) or "(no stated goal)"
            item.pop("agent_id", None)
            traces.append(item)
        return {"total": total, "offset": offset, "limit": limit, "traces": traces}

    # ---- graph slice ---------------------------------------------------------------------
    def graph(
        self,
        trace_ids: list[str],
        max_nodes: int = DEFAULT_MAX_NODES,
        include_inferred: bool = True,
    ) -> dict[str, Any]:
        ids = list(dict.fromkeys(trace_ids))
        if len(ids) > MAX_TRACES:
            raise CatalogError("too many traces requested")
        max_nodes = max(20, min(int(max_nodes), HARD_MAX_NODES))
        build = _Build(self.conn, max_nodes, actions_budget(len(ids), max_nodes))
        for tid in ids:
            build.add_trace(tid)
        build.add_shared()
        if include_inferred:
            build.add_inferred()
        payload = build.payload(ids)
        validate_trajectory_payload(payload)
        return payload

    # ---- playback steps ------------------------------------------------------------------
    def steps(
        self, trace_id: str, offset: int = 0, limit: int = 100, per_trace: int = MAX_ACTIONS_PER_TRACE
    ) -> dict[str, Any]:
        kind, _, raw = trace_id.partition(":")
        limit = max(1, min(int(limit), MAX_STEPS_PAGE))
        offset = max(0, int(offset))
        if kind == "session":
            row = self.conn.execute(
                "SELECT kind, item_count FROM sessions WHERE id = ?", (raw,)
            ).fetchone()
            if not row:
                raise CatalogError("unknown trace")
            if row["kind"] == "computer_use":
                rows = self.conn.execute(
                    "SELECT id, created_at, action, surface, work, detail, output, narration, "
                    "has_error, detail_path FROM turns WHERE session_id = ? "
                    "ORDER BY created_at, line LIMIT ? OFFSET ?", (raw, limit, offset),
                ).fetchall()  # fmt: skip
                table = "computer_use_turns"
            else:
                rows = self.conn.execute(
                    "SELECT id, created_at, role AS action, role AS surface, '' AS work, "
                    "text AS detail, NULL AS output, tools AS narration, 0 AS has_error, "
                    "text_path AS detail_path FROM messages WHERE session_id = ? "
                    "ORDER BY created_at, line LIMIT ? OFFSET ?", (raw, limit, offset),
                ).fetchall()  # fmt: skip
                table = "claude_code_messages"
            total = row["item_count"]
        elif kind == "episode":
            if not self.conn.execute("SELECT 1 FROM episodes WHERE id = ?", (raw,)).fetchone():
                raise CatalogError("unknown trace")
            rows = self.conn.execute(
                "SELECT id, created_at, speaker_type AS action, speaker_type AS surface, "
                "'' AS work, text AS detail, NULL AS output, agent_id AS narration, 0 AS has_error, "
                "text_path AS detail_path FROM messages WHERE episode_id = ? "
                "ORDER BY created_at, line LIMIT ? OFFSET ?", (raw, limit, offset),
            ).fetchall()  # fmt: skip
            total = self.conn.execute(
                "SELECT message_count FROM episodes WHERE id = ?", (raw,)
            ).fetchone()[0]
            table = "chat_messages"
        else:
            raise CatalogError("unknown trace")
        size, _count = bucket_plan(total, per_trace)
        out = []
        for i, r in enumerate(rows):
            seq = offset + i
            node = f"turn:{r['id']}" if size == 1 else f"run:{raw}:{seq // size}"
            if kind == "episode":
                node = f"message:{r['id']}"
            out.append({**dict(r), "seq": seq, "node_id": node,
                        "source_ref": SourceRef(table, r["id"]).to_dict()})  # fmt: skip
        return {"trace_id": trace_id, "total": total, "offset": offset, "bucket_size": size,
                "steps": out}  # fmt: skip


class _Build:
    """Accumulate nodes and edges under a hard node budget."""

    def __init__(self, conn: sqlite3.Connection, max_nodes: int, per_trace: int):
        self.conn = conn
        self.max_nodes = max_nodes
        self.per_trace = per_trace
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self.timeline: list[dict[str, Any]] = []
        self.aggregation: list[dict[str, Any]] = []
        self.hidden: list[dict[str, Any]] = []
        self.gaps: list[dict[str, Any]] = []
        self.artifact_owners: dict[str, set[str]] = {}
        self.owner_agent: dict[str, str | None] = {}
        self.artifact_rows: dict[str, list[sqlite3.Row]] = {}
        self.agent_names = {r[0]: r[1] for r in conn.execute("SELECT id, name FROM agents")}

    # -- primitives
    def room(self) -> int:
        return self.max_nodes - len(self.nodes)

    def node(self, node: GraphNode, at: str | None = None, trace: str | None = None) -> bool:
        if node.id in self.nodes:
            return True
        if self.room() <= 0:
            return False
        if trace:
            node.metadata["trace_id"] = trace
        if at:
            node.metadata["at"] = at
            self.timeline.append({"node_id": node.id, "at": at, "trace_id": trace})
        self.nodes[node.id] = node
        return True

    def edge(self, *args: Any, **kwargs: Any) -> None:
        e = GraphEdge(*args, **kwargs)
        if e.source in self.nodes and e.target in self.nodes:
            self.edges.append(e)

    def agent_node(self, agent_id: str | None) -> str | None:
        if not agent_id:
            return None
        nid = f"agent:{agent_id}"
        name = self.agent_names.get(agent_id)
        if name is None:
            self.gaps.append({"kind": "agent_row_missing", "agent_id": agent_id})
        self.node(GraphNode(nid, "agent", name or agent_id[:8], SourceRef("agents", agent_id),
                            metadata={"agent_id": agent_id}))  # fmt: skip
        return nid

    # -- traces
    def add_trace(self, trace_id: str) -> None:
        kind, _, raw = trace_id.partition(":")
        if kind == "session":
            self._add_session(raw, trace_id)
        elif kind == "episode":
            self._add_episode(raw, trace_id)
        else:
            raise CatalogError("unknown trace")
        self._add_goals(trace_id)
        self._add_language(trace_id)
        self._collect_artifacts(trace_id)

    def _add_session(self, sid: str, trace_id: str) -> None:
        s = self.conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
        if s is None:
            raise CatalogError("unknown trace")
        agent_nid = self.agent_node(s["agent_id"])
        label = _short(s["short_goal"] or s["goal_text"], 40) or f"session {sid[:8]}"
        snode = GraphNode(
            trace_id, "action", label, SourceRef(s["source_table"], sid),
            metadata={"kind": s["kind"], "agent_id": s["agent_id"], "started_at": s["started_at"],
                      "window_end": s["window_end"], "items": s["item_count"],
                      "stated_goal_present": s["goal_text"] is not None},
        )  # fmt: skip
        self.node(snode, s["started_at"], trace_id)
        self.owner_agent[trace_id] = s["agent_id"]
        if agent_nid:
            self.edge(agent_nid, trace_id, "recorded", "sessions.agent_id",
                      SourceRef(s["source_table"], sid), label="agent_session")  # fmt: skip
        if s["item_count"] == 0:
            self.gaps.append({"kind": "session_without_items", "trace_id": trace_id})
        if s["goal_text"] is not None:
            gid = f"intent:{sid}"
            gnode = GraphNode(
                gid, "goal", _short(s["short_goal"] or s["goal_text"], 60), SourceRef(s["source_table"], sid),
                claims=[{"field_path": "session_goal", "text": sanitize_text(s["goal_text"], 900)}],
                metadata={"role": "stated_intention", "note": "Stated intention. Not an outcome."},
            )  # fmt: skip
            if self.node(gnode, trace=trace_id):
                self.edge(trace_id, gid, "recorded", "sessions.session_goal",
                          SourceRef(s["source_table"], sid), label="stated_intention",
                          claims=gnode.claims)  # fmt: skip
        else:
            self.gaps.append({"kind": "session_goal_missing", "trace_id": trace_id})
        if s["kind"] == "computer_use":
            self._add_turn_actions(sid, trace_id, s["item_count"])
        else:
            self._add_cc_actions(sid, trace_id, s["item_count"])

    def _bucketed(self, trace_id: str, rows: list[sqlite3.Row], n: int, table: str) -> None:
        cap = self.per_trace
        size, count = bucket_plan(len(rows), cap)
        if size > 1:
            self.aggregation.append({
                "trace_id": trace_id, "items": n, "bucket_size": size, "nodes": count,
                "hides": "Each node summarizes consecutive items. Individual items stay in playback.",
            })  # fmt: skip
        if len(rows) < n:
            self.hidden.append({"trace_id": trace_id, "reason": "fetch_cap", "hidden": n - len(rows)})
        raw = trace_id.split(":", 1)[1]
        for k in range(count):
            chunk = rows[k * size : (k + 1) * size]
            first = chunk[0]
            if size == 1:
                nid = f"turn:{first['id']}"
                label = (first["action"] or "action").replace("_", " ")
                claims = (
                    [{"field_path": first["detail_path"] or "detail", "text": first["detail"]}]
                    if first["detail"] else []
                )
                meta = {"surface": first["surface"], "work": first["work"],
                        "seq": k, "has_error": bool(first["has_error"])}  # fmt: skip
            else:
                nid = f"run:{raw}:{k}"
                tally: dict[str, int] = {}
                for r in chunk:
                    tally[r["surface"]] = tally.get(r["surface"], 0) + 1
                top = sorted(tally.items(), key=lambda x: -x[1])[:3]
                label = f"{len(chunk)} items: " + ", ".join(f"{a} x{b}" for a, b in top)
                claims = [
                    {"field_path": r["detail_path"] or "detail", "text": r["detail"]}
                    for r in chunk if r["detail"]
                ][:3]
                meta = {"aggregated": True, "items": len(chunk), "surfaces": tally,
                        "first_seq": k * size, "last_seq": k * size + len(chunk) - 1,
                        "last_at": chunk[-1]["created_at"]}  # fmt: skip
            node = GraphNode(nid, "action", label, SourceRef(table, first["id"]), claims, meta)
            if self.node(node, first["created_at"], trace_id):
                self.edge(
                    trace_id, nid,
                    "recorded" if size == 1 else "rule_derived",
                    f"{table}.session_id" if size == 1 else "aggregate_by_time_order",
                    SourceRef(table, first["id"]), label="turn" if size == 1 else "turn_group",
                )
            else:
                self.hidden.append({"trace_id": trace_id, "reason": "node_budget",
                                    "hidden": count - k})  # fmt: skip
                break

    def _add_turn_actions(self, sid: str, trace_id: str, n: int) -> None:
        rows = self.conn.execute(
            "SELECT id, created_at, action, surface, work, detail, detail_path, has_error "
            "FROM turns WHERE session_id = ? ORDER BY created_at, line LIMIT ?",
            (sid, MAX_FETCH_ITEMS),
        ).fetchall()
        if rows:
            self._bucketed(trace_id, rows, n, "computer_use_turns")

    def _add_cc_actions(self, sid: str, trace_id: str, n: int) -> None:
        rows = self.conn.execute(
            "SELECT id, created_at, COALESCE(role, 'message') AS action, role AS surface, "
            "'' AS work, text AS detail, text_path AS detail_path, 0 AS has_error "
            "FROM messages WHERE session_id = ? ORDER BY created_at, line LIMIT ?",
            (sid, MAX_FETCH_ITEMS),
        ).fetchall()
        if rows:
            self._bucketed(trace_id, rows, n, "claude_code_messages")

    def _add_episode(self, eid: str, trace_id: str) -> None:
        e = self.conn.execute("SELECT * FROM episodes WHERE id = ?", (eid,)).fetchone()
        if e is None:
            raise CatalogError("unknown trace")
        label = f"#{e['room_name'] or e['room_id'][:8]} ({e['message_count']} msgs)"
        enode = GraphNode(
            trace_id, "action", label, SourceRef("chat_messages", e["first_message_id"]),
            metadata={"kind": "chat_episode", "started_at": e["started_at"],
                      "ended_at": e["ended_at"], "items": e["message_count"],
                      "rule": "episode_gap_minutes"},
        )  # fmt: skip
        self.node(enode, e["started_at"], trace_id)
        members = self.conn.execute(
            "SELECT agent_id, n_messages, first_message_id FROM episode_members "
            "WHERE episode_id = ? ORDER BY n_messages DESC, agent_id", (eid,),
        ).fetchall()  # fmt: skip
        for m in members:
            if m["agent_id"].startswith("user:"):
                continue
            nid = self.agent_node(m["agent_id"])
            if nid:
                self.edge(nid, trace_id, "recorded", "chat_messages.agent_speaker_id",
                          SourceRef("chat_messages", m["first_message_id"]),
                          label=f"spoke_{m['n_messages']}_msgs")  # fmt: skip
        rows = self.conn.execute(
            "SELECT id, agent_id, speaker_id, speaker_type, created_at, text FROM messages "
            "WHERE episode_id = ? ORDER BY created_at, line LIMIT ?", (eid, MESSAGES_PER_EPISODE),
        ).fetchall()  # fmt: skip
        if e["message_count"] > len(rows):
            self.aggregation.append({
                "trace_id": trace_id, "items": e["message_count"], "bucket_size": 1,
                "nodes": len(rows),
                "hides": f"Only the first {len(rows)} messages are drawn. All stay in playback.",
            })  # fmt: skip
        for r in rows:
            mid = f"message:{r['id']}"
            who = self.agent_names.get(r["agent_id"] or "", r["speaker_id"] or "unknown")
            claims = [{"field_path": "content", "text": r["text"] or ""}]
            if self.node(GraphNode(mid, "artifact", f"{who}: {_short(r['text'], 40)}",
                                   SourceRef("chat_messages", r["id"]), claims,
                                   {"speaker_type": r["speaker_type"]}), r["created_at"], trace_id):  # fmt: skip
                self.edge(trace_id, mid, "rule_derived", "episode_gap_minutes",
                          SourceRef("chat_messages", r["id"]), label="episode_message",
                          claims=claims)  # fmt: skip
        self.owner_agent[trace_id] = None

    # -- goals
    def _add_goals(self, trace_id: str) -> None:
        rows = self.conn.execute(
            "SELECT l.goal_id, l.overlap, g.label, g.description, g.scope, g.source_table, "
            "g.starts_at, g.effective_end FROM goal_links l LEFT JOIN goals g ON g.id = l.goal_id "
            "WHERE l.owner_id = ? ORDER BY l.goal_id", (trace_id,),
        ).fetchall()  # fmt: skip
        for r in rows:
            gid = f"goal:{r['goal_id']}"
            if r["goal_id"] == UNKNOWN_GOAL:
                gnode = GraphNode(
                    gid, "goal", "unknown goal", SourceRef("goal_links", UNKNOWN_GOAL),
                    claims=[{"field_path": "goal_links", "text": "No goal window covers this trace."}],
                    metadata={"role": "unknown_goal"},
                )  # fmt: skip
                src = SourceRef("goal_links", trace_id)
            else:
                gnode = GraphNode(
                    gid, "goal", r["label"] or r["goal_id"][:8], SourceRef(r["source_table"], r["goal_id"]),
                    claims=[{"field_path": "goal", "text": sanitize_text(r["description"] or r["label"], 600)}],
                    metadata={"role": "stated_goal", "scope": r["scope"], "starts_at": r["starts_at"],
                              "ends_at": r["effective_end"], "note": "Stated goal. Not an outcome."},
                )  # fmt: skip
                src = SourceRef(r["source_table"], r["goal_id"])
            if self.node(gnode):
                self.edge(trace_id, gid, "rule_derived", f"temporal_window:{r['overlap']}", src,
                          label=TEMPORAL_LABEL, note=TEMPORAL_NOTE)  # fmt: skip

    # -- language
    def _add_language(self, trace_id: str) -> None:
        rows = self.conn.execute(
            "SELECT term, kind, n_owners, n_agents, score, source_table, source_id, field_path "
            "FROM language_links WHERE owner_id = ? ORDER BY score DESC, kind DESC, term LIMIT ?",
            (trace_id, LANGUAGE_PER_TRACE),
        ).fetchall()  # fmt: skip
        for r in rows:
            nid = f"lang:{r['kind']}:{r['term']}"
            node = GraphNode(
                nid, "artifact", f"\u201c{r['term']}\u201d" if r["kind"] == "phrase" else r["term"],
                SourceRef(r["source_table"], r["source_id"]),
                metadata={"artifact_kind": f"language_{r['kind']}", "traces_in_index": r["n_owners"],
                          "agents_in_index": r["n_agents"], "note": LANGUAGE_NOTE},
            )  # fmt: skip
            if self.node(node):
                self.edge(trace_id, nid, "rule_derived", "shared_rare_language",
                          SourceRef(r["source_table"], r["source_id"]), score=r["score"],
                          label="uses_wording", note=LANGUAGE_NOTE,
                          claims=[{"field_path": r["field_path"], "text": f"{r['kind']}: {r['term']}"}])  # fmt: skip

    # -- artifacts
    def _collect_artifacts(self, trace_id: str) -> None:
        rows = self.conn.execute(
            "SELECT * FROM artifacts WHERE owner_id = ? ORDER BY mentions DESC, kind, identifier",
            (trace_id,),
        ).fetchall()
        self.artifact_rows[trace_id] = rows
        for r in rows:
            key = f"artifact:{r['kind']}:{r['scope']}:{r['identifier']}"
            self.artifact_owners.setdefault(key, set()).add(trace_id)

    def add_shared(self) -> None:
        """Add artifact nodes. Artifacts used by 2 or more selected traces come first."""
        shown: dict[str, int] = {}
        order: list[tuple[int, int, str, sqlite3.Row]] = []
        for trace_id, rows in self.artifact_rows.items():
            for r in rows:
                key = f"artifact:{r['kind']}:{r['scope']}:{r['identifier']}"
                order.append((-len(self.artifact_owners[key]), -r["mentions"], trace_id, r))
        order.sort(key=lambda t: (t[0], t[1], t[2], t[3]["kind"], t[3]["identifier"]))
        hidden = 0
        for neg_shared, _m, trace_id, r in order:
            key = f"artifact:{r['kind']}:{r['scope']}:{r['identifier']}"
            if neg_shared == -1 and shown.get(trace_id, 0) >= ARTIFACTS_PER_TRACE:
                hidden += 1
                continue
            owners = self.artifact_owners[key]
            if key not in self.nodes:
                agents_in_index = self.conn.execute(
                    "SELECT COUNT(DISTINCT agent_id) FROM artifacts WHERE kind = ? AND identifier = ? "
                    "AND scope = ?", (r["kind"], r["identifier"], r["scope"]),
                ).fetchone()[0]
                meta = {"artifact_kind": r["kind"], "scope": r["scope"], "mentions": r["mentions"],
                        "agents_in_index": agents_in_index}  # fmt: skip
                if len(owners) > 1:
                    meta["selected_traces"] = len(owners)
                    meta["note"] = SHARED_NOTE
                node = GraphNode(
                    key, "artifact", r["identifier"][-48:] if r["kind"] != "file" else r["identifier"][-40:],
                    SourceRef(r["source_table"], r["source_id"]),
                    claims=[{"field_path": r["field_path"], "text": r["identifier"]}], metadata=meta,
                )  # fmt: skip
                if not self.node(node, r["first_at"], trace_id):
                    hidden += 1
                    continue
            shown[trace_id] = shown.get(trace_id, 0) + 1
            self.edge(trace_id, key, "rule_derived", f"extract_{r['kind']}_from_text",
                      SourceRef(r["source_table"], r["source_id"]), label="mentions",
                      note="A mention in recorded text. It does not show who made or changed it.",
                      claims=[{"field_path": r["field_path"], "text": r["identifier"]}])  # fmt: skip
        if hidden:
            self.hidden.append({"reason": "artifact_cap_or_budget", "hidden": hidden})

    def add_inferred(self) -> None:
        for r in self.conn.execute(
            "SELECT l.*, r.model FROM llm_links l JOIN llm_runs r ON r.id = l.run_id "
            "ORDER BY l.id LIMIT 500"
        ):
            if r["source_node"] in self.nodes and r["target_node"] in self.nodes:
                self.edges.append(GraphEdge(
                    r["source_node"], r["target_node"], "inferred", f"llm:{r['model']}",
                    SourceRef("llm_links", r["id"]), label=r["relation"], note=r["rationale"],
                    claims=[{"field_path": "llm.rationale", "text": r["rationale"]}],
                ))  # fmt: skip

    # -- output
    def payload(self, trace_ids: list[str]) -> dict[str, Any]:
        self.timeline.sort(key=lambda t: (t["at"] or "", t["node_id"]))
        for i, t in enumerate(self.timeline):
            t["seq"] = i
        tiers: dict[str, int] = {}
        for n in self.nodes.values():
            tiers[n.tier] = tiers.get(n.tier, 0) + 1
        classes: dict[str, int] = {}
        for e in self.edges:
            classes[e.evidence_class] = classes.get(e.evidence_class, 0) + 1
        return {
            "schema_version": SCHEMA_VERSION,
            "meta": {
                "traces": trace_ids,
                "nodes_count": len(self.nodes),
                "edges_count": len(self.edges),
                "max_nodes": self.max_nodes,
                "actions_per_trace": self.per_trace,
                "is_bounded": bool(self.hidden or self.aggregation),
                "tiers": tiers,
                "evidence_classes": classes,
                "aggregation": self.aggregation,
                "hidden": self.hidden,
                "gaps": self.gaps,
                "statement": "Recorded evidence only. The goal tier shows stated intention.",
            },
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "timeline": self.timeline,
        }

