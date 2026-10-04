"""Streaming importer: raw `.jsonl.gz` archives into the SQLite index (schema version 2).

Each archive is read once per import, one line at a time. No table is loaded into memory.
Each stage writes a checkpoint. A stage with a `complete` checkpoint is skipped on re-run.
A stage without one is cleared and rebuilt. Diagnostics hold counts only, never record values.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import sqlite3
import sys
import time
import zlib
from collections import Counter
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import db  # noqa: E402
from contract import sanitize_text  # noqa: E402
from extract import MessageFacts, extract_artifacts, extract_cc_message, extract_turn  # noqa: E402

BATCH = 5000
COMMIT_EVERY = 50_000
PROGRESS_EVERY = 100_000
ARTIFACT_FLUSH = 150_000
DISK_MARGIN = 1 << 30
# Heuristic: index bytes per compressed archive byte. The real ratio is measured and reported.
DISK_FACTOR = {
    "computer_use_turns": 0.7, "claude_code_messages": 3.0, "chat_messages": 2.0, "events": 1.0,
}  # fmt: skip

INGEST_STAGES = (
    "agents", "chat_rooms", "village_goals", "agent_goals", "computer_use_sessions",
    "claude_code_sessions", "computer_use_turns", "claude_code_messages", "chat_messages",
    "events",
)  # fmt: skip
OPTIONAL_STAGES = ("agent_memories",)
DERIVED_STAGES = ("sessions_window", "mirrors", "episodes", "goal_links", "language")

_TS_FAST = len("2026-03-18 20:40:06")


def norm_ts(value: Any) -> str | None:
    """Return `YYYY-MM-DD HH:MM:SS.ffffff` (UTC) or None. Sorts as text."""
    if not isinstance(value, str) or len(value) < _TS_FAST:
        return None
    base, _, frac = value.removesuffix("Z").partition(".")
    if (
        len(base) != _TS_FAST
        or base[4] != "-" or base[7] != "-" or base[10] not in " T"
        or base[13] != ":" or base[16] != ":"
    ):
        return None
    digits = base[:4] + base[5:7] + base[8:10] + base[11:13] + base[14:16] + base[17:19]
    if not digits.isdigit() or (frac and not frac.isdigit()):
        return None
    return f"{base[:10]} {base[11:]}.{frac.ljust(6, '0')[:6]}"


def clean_goal(value: Any, limit: int = 2000) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return sanitize_text(value, limit)


class Reader:
    """Stream one archive. Count problems instead of raising."""

    def __init__(self, path: Path, limit: int | None = None):
        self.path = path
        self.limit = limit
        self.lines = 0
        self.bad_json = 0
        self.not_object = 0
        self.damaged = False
        self.missing = not path.is_file()

    def __iter__(self) -> Iterator[tuple[int, dict[str, Any]]]:
        if self.missing:
            return
        try:
            with gzip.open(self.path, "rt", encoding="utf-8", errors="replace") as handle:
                for line_no, line in enumerate(handle, start=1):
                    if self.limit is not None and self.lines >= self.limit:
                        return
                    line = line.strip()
                    if not line:
                        continue
                    self.lines += 1
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        self.bad_json += 1
                        continue
                    if not isinstance(record, dict):
                        self.not_object += 1
                        continue
                    yield line_no, record
        except (gzip.BadGzipFile, EOFError, OSError, zlib.error):
            self.damaged = True


class Stat:
    def __init__(self, table: str):
        self.table = table
        self.read = 0
        self.indexed = 0
        self.skipped: Counter[str] = Counter()
        self.notes: Counter[str] = Counter()
        self.shapes: Counter[tuple[str, bool]] = Counter()
        self.started = time.time()

    def skip(self, reason: str) -> None:
        self.skipped[reason] += 1


def _s(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


class TrajectoryImporter:
    def __init__(
        self,
        data_dir: Path,
        db_path: Path,
        limit: int | None = None,
        progress: Callable[[str], None] | None = print,
        disk_check: bool = True,
        rebuild: bool = False,
    ):
        self.data_dir = Path(data_dir)
        self.db_path = Path(db_path)
        self.limit = limit
        self.progress = progress or (lambda _msg: None)
        self.disk_check = disk_check
        if rebuild:
            for suffix in ("", "-wal", "-shm"):
                Path(str(self.db_path) + suffix).unlink(missing_ok=True)
        self.conn = db.connect(self.db_path, create=True)
        self.manifest = self._read_manifest()
        self.ran: list[str] = []

    # ---- helpers -------------------------------------------------------------------------
    def _read_manifest(self) -> dict[str, int]:
        path = self.data_dir / "manifest.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        counts = data.get("rowCounts") or data.get("tables") or {}
        return {k: v for k, v in counts.items() if isinstance(v, int)}

    def checkpoint_status(self, table: str) -> str | None:
        row = self.conn.execute(
            "SELECT status FROM checkpoints WHERE table_name = ?", (table,)
        ).fetchone()
        return row[0] if row else None

    def _write_checkpoint(self, stat: Stat, status: str) -> None:
        skipped = sum(stat.skipped.values())
        reasons = dict(stat.skipped)
        reasons.update({f"note:{k}": v for k, v in stat.notes.items()})
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO checkpoints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    stat.table, status, stat.read, stat.indexed, skipped,
                    json.dumps(reasons, sort_keys=True), self.manifest.get(stat.table),
                    round(time.time() - stat.started, 2),
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                ),
            )  # fmt: skip
            self.conn.execute("DELETE FROM shape_counts WHERE table_name = ?", (stat.table,))
            self.conn.executemany(
                "INSERT INTO shape_counts VALUES (?, ?, ?, ?)",
                [(stat.table, shape, int(ok), n) for (shape, ok), n in sorted(stat.shapes.items())],
            )

    def _estimate_disk(self, table: str, path: Path) -> None:
        if table not in DISK_FACTOR or not path.is_file():
            return
        estimate = int(path.stat().st_size * DISK_FACTOR[table])
        free = shutil.disk_usage(self.db_path.parent).free
        self.progress(
            f"[{table}] disk estimate up to {estimate >> 20} MB; free {free >> 20} MB (heuristic)"
        )
        if self.disk_check and estimate + DISK_MARGIN > free:
            raise OSError(f"not enough free disk for stage {table}")

    def _tick(self, stat: Stat) -> None:
        if stat.read % PROGRESS_EVERY == 0:
            rate = stat.read / max(time.time() - stat.started, 0.001)
            self.progress(
                f"[{stat.table}] read {stat.read:,} indexed {stat.indexed:,} ({rate:,.0f} rows/s)"
            )

    def _insert(self, sql: str, batch: list[tuple]) -> None:
        if batch:
            self.conn.executemany(sql, batch)
            batch.clear()

    # ---- stage runner --------------------------------------------------------------------
    def run_stage(self, table: str, force: bool = False) -> str:
        status = self.checkpoint_status(table)
        if status == "complete" and not force:
            self.progress(f"[{table}] complete checkpoint found; skipped")
            return "skipped"
        path = self.data_dir / f"{table}.jsonl.gz"
        stat = Stat(table)
        reader = Reader(path, self.limit)
        if reader.missing:
            stat.skip("missing_table")
            self._write_checkpoint(stat, "missing")
            self.progress(f"[{table}] archive not found")
            return "missing"
        self._estimate_disk(table, path)
        handler = getattr(self, f"_stage_{table}")
        self._clear(table)
        handler(reader, stat)
        stat.skipped["bad_json"] += reader.bad_json
        stat.skipped["not_object"] += reader.not_object
        if reader.damaged:
            stat.skipped["damaged_gzip"] += 1
        stat.read = reader.lines
        stat.skipped = Counter({k: v for k, v in stat.skipped.items() if v})
        self.conn.commit()
        self._write_checkpoint(stat, "partial" if reader.damaged else "complete")
        self.ran.append(table)
        self.progress(
            f"[{table}] done: read {stat.read:,} indexed {stat.indexed:,} "
            f"skipped {sum(stat.skipped.values()):,} in {time.time() - stat.started:.1f}s"
        )
        return "partial" if reader.damaged else "complete"

    def _clear(self, table: str) -> None:
        owned = {
            "agents": ("agents", None), "chat_rooms": ("rooms", None),
            "village_goals": ("goals", "scope = 'village'"),
            "agent_goals": ("goals", "scope = 'agent'"),
            "computer_use_sessions": ("sessions", "kind = 'computer_use'"),
            "claude_code_sessions": ("sessions", "kind = 'claude_code'"),
            "computer_use_turns": ("turns", None),
            "claude_code_messages": ("messages", "source_table = 'claude_code_messages'"),
            "chat_messages": ("messages", "source_table = 'chat_messages'"),
            "events": ("events", None),
        }  # fmt: skip
        target, where = owned[table]
        with self.conn:
            self.conn.execute(f"DELETE FROM {target}" + (f" WHERE {where}" if where else ""))
            sources = {
                "computer_use_turns": "computer_use_turns",
                "claude_code_messages": "claude_code_messages",
            }
            if table in sources:
                self.conn.execute("DELETE FROM artifacts WHERE source_table = ?", (sources[table],))

    # ---- small tables --------------------------------------------------------------------
    def _stage_agents(self, reader: Reader, stat: Stat) -> None:
        for line, rec in reader:
            aid = _s(rec.get("id"))
            if not aid:
                stat.skip("missing_id")
                continue
            self.conn.execute(
                "INSERT OR REPLACE INTO agents VALUES (?, ?, ?, ?)",
                (aid, sanitize_text(rec.get("name") or aid, 120), _s(rec.get("model_string")), line),
            )
            stat.indexed += 1

    def _stage_chat_rooms(self, reader: Reader, stat: Stat) -> None:
        for line, rec in reader:
            rid = _s(rec.get("id"))
            if not rid:
                stat.skip("missing_id")
                continue
            self.conn.execute(
                "INSERT OR REPLACE INTO rooms VALUES (?, ?, ?)",
                (rid, sanitize_text(rec.get("name") or "", 120) or None, line),
            )
            stat.indexed += 1

    def _stage_village_goals(self, reader: Reader, stat: Stat) -> None:
        for line, rec in reader:
            gid = _s(rec.get("id"))
            text = clean_goal(rec.get("goal"), 1500)
            if not gid:
                stat.skip("missing_id")
                continue
            if text is None:
                stat.notes["empty_goal_text"] += 1
            label = (text or "(no goal text)").strip().splitlines()[0][:90]
            self.conn.execute(
                "INSERT OR REPLACE INTO goals VALUES (?, 'village', NULL, ?, ?, ?, ?, NULL, "
                "'village_goals', ?)",
                (gid, label, text, norm_ts(rec.get("start_time")), norm_ts(rec.get("end_time")), line),
            )
            stat.indexed += 1

    def _stage_agent_goals(self, reader: Reader, stat: Stat) -> None:
        for line, rec in reader:
            gid = _s(rec.get("id"))
            if not gid:
                stat.skip("missing_id")
                continue
            name = clean_goal(rec.get("name"), 400)
            label = _s(rec.get("short_name")) or (name or "(no goal text)")[:90]
            desc = clean_goal(rec.get("description"), 1500) or name
            self.conn.execute(
                "INSERT OR REPLACE INTO goals VALUES (?, 'agent', ?, ?, ?, ?, ?, NULL, "
                "'agent_goals', ?)",
                (
                    gid, _s(rec.get("agent_id")), sanitize_text(label, 90), desc,
                    norm_ts(rec.get("start_time")), norm_ts(rec.get("end_time")), line,
                ),
            )  # fmt: skip
            if not _s(rec.get("agent_id")):
                stat.notes["no_agent_id"] += 1
            stat.indexed += 1

    # ---- sessions ------------------------------------------------------------------------
    def _stage_computer_use_sessions(self, reader: Reader, stat: Stat) -> None:
        batch: list[tuple] = []
        sql = "INSERT OR REPLACE INTO sessions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        for line, rec in reader:
            sid = _s(rec.get("id"))
            if not sid:
                stat.skip("missing_id")
                continue
            goal = clean_goal(rec.get("session_goal"))
            if goal is None:
                stat.notes["no_session_goal"] += 1
            created = norm_ts(rec.get("created_at"))
            batch.append((
                sid, "computer_use", _s(rec.get("agent_id")), None, goal,
                clean_goal(rec.get("short_displayed_session_goal"), 160), created,
                norm_ts(rec.get("updated_at")), None, None, None, 0,
                "computer_use_sessions", line,
            ))  # fmt: skip
            stat.indexed += 1
            if len(batch) >= BATCH:
                self._insert(sql, batch)
        self._insert(sql, batch)
        db.create_indexes(self.conn, "sessions")

    def _stage_claude_code_sessions(self, reader: Reader, stat: Stat) -> None:
        sql = "INSERT OR REPLACE INTO sessions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        for line, rec in reader:
            sid = _s(rec.get("id"))
            if not sid:
                stat.skip("missing_id")
                continue
            if not _s(rec.get("sdk_session_id")):
                stat.notes["no_sdk_session_id"] += 1
            self.conn.execute(
                sql,
                (
                    sid, "claude_code", _s(rec.get("agent_id")), _s(rec.get("sdk_session_id")),
                    None, None, norm_ts(rec.get("created_at")), norm_ts(rec.get("updated_at")),
                    None, None, None, 0, "claude_code_sessions", line,
                ),
            )  # fmt: skip
            stat.indexed += 1
        db.create_indexes(self.conn, "sessions")

    # ---- artifacts -----------------------------------------------------------------------
    _ARTIFACT_SQL = """
        INSERT INTO artifacts (owner_id, kind, identifier, scope, agent_id, first_at,
                               source_table, source_id, field_path, mentions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (owner_id, kind, identifier, scope) DO UPDATE SET
            mentions = mentions + excluded.mentions,
            source_id = CASE WHEN excluded.first_at < first_at THEN excluded.source_id
                             ELSE source_id END,
            field_path = CASE WHEN excluded.first_at < first_at THEN excluded.field_path
                              ELSE field_path END,
            first_at = MIN(first_at, excluded.first_at)
    """

    def _add_artifacts(
        self,
        agg: dict[tuple[str, str, str, str], list],
        owner: str,
        agent_id: str | None,
        texts: list[tuple[str, str]],
        when: str | None,
        table: str,
        source_id: str,
        extra: list[tuple[str, str, str]] | None = None,
    ) -> None:
        found: list[tuple[str, str, str, str]] = []
        for path, text in texts:
            if text:
                for kind, ident, scope in extract_artifacts(text, agent_id):
                    found.append((kind, ident, scope, path))
        for kind, ident, scope in extra or []:
            found.append((kind, ident, scope, "tool_input.title"))
        seen: set[tuple[str, str, str]] = set()
        for kind, ident, scope, path in found:
            key3 = (kind, ident, scope)
            if key3 in seen:
                continue
            seen.add(key3)
            key = (owner, kind, ident, scope)
            slot = agg.get(key)
            if slot is None:
                agg[key] = [when or "", table, source_id, path, 1, agent_id]
            else:
                slot[4] += 1

    def _flush_artifacts(self, agg: dict, force: bool = False) -> None:
        if not agg or (not force and len(agg) < ARTIFACT_FLUSH):
            return
        rows = [
            (o, k, i, sc, v[5], v[0], v[1], v[2], v[3], v[4]) for (o, k, i, sc), v in agg.items()
        ]
        for start in range(0, len(rows), BATCH):
            self.conn.executemany(self._ARTIFACT_SQL, rows[start : start + BATCH])
        self.conn.commit()
        agg.clear()

    # ---- turns ---------------------------------------------------------------------------
    def _stage_computer_use_turns(self, reader: Reader, stat: Stat) -> None:
        agent_of = {
            r[0]: r[1] for r in self.conn.execute(
                "SELECT id, agent_id FROM sessions WHERE kind = 'computer_use'"
            )
        }  # fmt: skip
        per_session: dict[str, list] = {}
        agg: dict[tuple[str, str, str, str], list] = {}
        batch: list[tuple] = []
        sql = "INSERT INTO turns VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
        for line, rec in reader:
            stat.read += 1
            self._tick(stat)
            tid, sid = _s(rec.get("id")), _s(rec.get("session_id"))
            if not tid:
                stat.skip("missing_id")
                continue
            if not sid:
                stat.skip("missing_session_id")
                continue
            facts = extract_turn(rec)
            stat.shapes[(f"agent_messages:{facts.shape}", facts.shape != "unsupported")] += 1
            if facts.shape == "unsupported":
                stat.notes["unsupported_agent_messages"] += 1
            when = norm_ts(rec.get("created_at"))
            if when is None:
                stat.notes["bad_created_at"] += 1
            batch.append((
                line, tid, sid, when, facts.action, facts.surface, facts.work,
                facts.detail or None, facts.detail_path or None, facts.output or None,
                facts.narration or None, int(facts.has_error), facts.shape,
            ))  # fmt: skip
            stat.indexed += 1
            slot = per_session.get(sid)
            if slot is None:
                per_session[sid] = [1, when, when]
            else:
                slot[0] += 1
                if when and (slot[1] is None or when < slot[1]):
                    slot[1] = when
                if when and (slot[2] is None or when > slot[2]):
                    slot[2] = when
            if sid in agent_of:
                self._add_artifacts(
                    agg, f"session:{sid}", agent_of[sid], facts.artifact_texts, when,
                    "computer_use_turns", tid,
                )
            else:
                stat.notes["orphan_turn_artifacts_skipped"] += 1
            if len(batch) >= BATCH:
                self._insert(sql, batch)
            if stat.indexed % COMMIT_EVERY == 0:
                self._flush_artifacts(agg)
                self.conn.commit()
        self._insert(sql, batch)
        self._flush_artifacts(agg, force=True)
        self._apply_session_stats(per_session, "computer_use")
        db.create_indexes(self.conn, "turns", "artifacts")

    def _apply_session_stats(self, per_session: dict[str, list], kind: str) -> None:
        rows = [(v[0], v[1], v[2], k, kind) for k, v in per_session.items()]
        for start in range(0, len(rows), BATCH):
            self.conn.executemany(
                "UPDATE sessions SET item_count = ?, first_turn_at = ?, last_turn_at = ? "
                "WHERE id = ? AND kind = ?",
                rows[start : start + BATCH],
            )
        self.conn.commit()

    # ---- claude code messages ------------------------------------------------------------
    def _stage_claude_code_messages(self, reader: Reader, stat: Stat) -> None:
        sess = {
            r[0]: (r[1], r[2]) for r in self.conn.execute(
                "SELECT sdk_session_id, id, agent_id FROM sessions "
                "WHERE kind = 'claude_code' AND sdk_session_id IS NOT NULL"
            )
        }  # fmt: skip
        per_session: dict[str, list] = {}
        agg: dict[tuple[str, str, str, str], list] = {}
        batch: list[tuple] = []
        sql = "INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        for line, rec in reader:
            stat.read += 1
            self._tick(stat)
            mid = _s(rec.get("id"))
            if not mid:
                stat.skip("missing_id")
                continue
            facts: MessageFacts = extract_cc_message(rec)
            stat.shapes[(f"content:{facts.shape}", facts.shape != "unsupported")] += 1
            if facts.shape == "unsupported":
                stat.notes["unsupported_content"] += 1
            ref = _s(rec.get("sdk_session_id"))
            sid, sess_agent = sess.get(ref, (None, None)) if ref else (None, None)
            if ref and sid is None:
                stat.notes["orphan_message"] += 1
            agent = _s(rec.get("agent_id")) or sess_agent
            when = norm_ts(rec.get("created_at"))
            batch.append((
                mid, "claude_code_messages", line, sid, ref, agent, agent, "agent", None, None,
                facts.role, when, facts.text or None, facts.text_path,
                json.dumps(facts.tools) if facts.tools else None, facts.shape,
            ))  # fmt: skip
            stat.indexed += 1
            if sid:
                slot = per_session.get(sid)
                if slot is None:
                    per_session[sid] = [1, when, when]
                else:
                    slot[0] += 1
                    if when and (slot[1] is None or when < slot[1]):
                        slot[1] = when
                    if when and (slot[2] is None or when > slot[2]):
                        slot[2] = when
                self._add_artifacts(
                    agg, f"session:{sid}", agent, facts.artifact_texts, when,
                    "claude_code_messages", mid,
                    extra=[("title", t, "global") for t in facts.titles],
                )
            if len(batch) >= BATCH:
                self._insert(sql, batch)
            if stat.indexed % COMMIT_EVERY == 0:
                self._flush_artifacts(agg)
                self.conn.commit()
        self._insert(sql, batch)
        self._flush_artifacts(agg, force=True)
        self._apply_session_stats(per_session, "claude_code")
        db.create_indexes(self.conn, "messages", "artifacts")

    # ---- chat ----------------------------------------------------------------------------
    def _stage_chat_messages(self, reader: Reader, stat: Stat) -> None:
        batch: list[tuple] = []
        sql = "INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        for line, rec in reader:
            stat.read += 1
            self._tick(stat)
            mid = _s(rec.get("id"))
            if not mid:
                stat.skip("missing_id")
                continue
            agent = _s(rec.get("agent_speaker_id"))
            speaker = agent or _s(rec.get("user_speaker_id"))
            stype = _s(rec.get("speaker_type"))
            if speaker is None:
                stat.notes["no_speaker"] += 1
            content = rec.get("content")
            if not isinstance(content, str):
                stat.notes["non_text_content"] += 1
            stat.shapes[("content:plain_text" if isinstance(content, str) else "content:empty", True)] += 1
            batch.append((
                mid, "chat_messages", line, None, None, agent, speaker, stype,
                _s(rec.get("room_id")), None, stype, norm_ts(rec.get("created_at")),
                sanitize_text(content, 1500) or None, "content", None, "plain_text",
            ))  # fmt: skip
            stat.indexed += 1
            if len(batch) >= BATCH:
                self._insert(sql, batch)
            if stat.indexed % COMMIT_EVERY == 0:
                self.conn.commit()
        self._insert(sql, batch)
        db.create_indexes(self.conn, "messages")

    # ---- events --------------------------------------------------------------------------
    _EVENT_KEYS = (
        "content", "summary", "sessionGoal", "nextSessionGoal", "query", "answerToQuery",
        "shortDisplayedSessionGoal", "newName",
    )  # fmt: skip

    def _stage_events(self, reader: Reader, stat: Stat) -> None:
        batch: list[tuple] = []
        sql = "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,0)"
        for line, rec in reader:
            stat.read += 1
            self._tick(stat)
            eid = _s(rec.get("id"))
            if not eid:
                stat.skip("missing_id")
                continue
            data = rec.get("data")
            if not isinstance(data, dict):
                stat.notes["non_object_data"] += 1
                data = {}
            action = _s(data.get("actionType")) or "UNKNOWN"
            if action == "UNKNOWN":
                stat.notes["no_action_type"] += 1
            stat.shapes[(f"actionType:{action}", True)] += 1
            raw_index = rec.get("event_index")
            index = raw_index if isinstance(raw_index, int) else None
            if index is None:
                stat.notes["no_event_index"] += 1
            parts = [
                f"{k}: {data[k]}" for k in self._EVENT_KEYS
                if isinstance(data.get(k), str) and data[k]
            ][:2]  # fmt: skip
            if isinstance(data.get("seconds"), (int, float)):
                parts.append(f"seconds: {data['seconds']}")
            agent = _s(data.get("agentId")) or (
                _s(data.get("speakerId")) if data.get("speakerType") == "agent" else None
            )
            batch.append((
                eid, line, index, norm_ts(rec.get("created_at")), action, agent,
                _s(data.get("computerUseSessionId")),
                _s(data.get("chatMessageId")) or _s(data.get("messageId")),
                _s(data.get("roomId")), sanitize_text(" | ".join(parts), 300) or None,
            ))  # fmt: skip
            stat.indexed += 1
            if len(batch) >= BATCH:
                self._insert(sql, batch)
            if stat.indexed % COMMIT_EVERY == 0:
                self.conn.commit()
        self._insert(sql, batch)
        db.create_indexes(self.conn, "events")

    # ---- optional memory stage -----------------------------------------------------------
    def _stage_agent_memories(self, reader: Reader, stat: Stat) -> None:
        """Count rows only. Memories are claims. The text is not indexed in this version."""
        for _line, _rec in reader:
            stat.read += 1
            self._tick(stat)
            stat.skip("not_indexed_optional_stage")

    # ---- derived stages ------------------------------------------------------------------
    def run_derived(self, force: bool = False) -> None:
        import episodes
        import goals
        import language

        steps: dict[str, Callable[[sqlite3.Connection], dict[str, int]]] = {
            "sessions_window": self._derive_sessions_window,
            "mirrors": self._derive_mirrors,
            "episodes": episodes.build_episodes,
            "goal_links": goals.build_goal_links,
            "language": language.build_language_links,
        }
        redo = force or bool(self.ran)
        for name in DERIVED_STAGES:
            key = f"derived:{name}"
            if not redo and self.checkpoint_status(key) == "complete":
                continue
            stat = Stat(key)
            counts = steps[name](self.conn)
            self.conn.commit()
            stat.read = stat.indexed = sum(counts.values())
            stat.notes.update({k: v for k, v in counts.items() if v})
            self._write_checkpoint(stat, "complete")
            self.progress(f"[{key}] {counts}")

    @staticmethod
    def _derive_sessions_window(conn: sqlite3.Connection) -> dict[str, int]:
        conn.execute(
            "UPDATE sessions SET window_end = MAX(COALESCE(last_turn_at, ''), "
            "COALESCE(updated_at, ''), COALESCE(started_at, ''))"
        )
        conn.execute("UPDATE sessions SET window_end = NULL WHERE window_end = ''")
        n = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        return {"sessions": n}

    @staticmethod
    def _derive_mirrors(conn: sqlite3.Connection) -> dict[str, int]:
        conn.execute("UPDATE events SET mirrored = 0")
        conn.execute(
            "UPDATE events SET mirrored = 1 WHERE message_id IS NOT NULL AND EXISTS "
            "(SELECT 1 FROM messages m WHERE m.id = events.message_id "
            "AND m.source_table = 'chat_messages')"
        )
        mirrored = conn.execute("SELECT COUNT(*) FROM events WHERE mirrored = 1").fetchone()[0]
        unmatched = conn.execute(
            "SELECT COUNT(*) FROM events WHERE message_id IS NOT NULL AND mirrored = 0"
        ).fetchone()[0]
        return {"mirrored_events": mirrored, "unmatched_message_events": unmatched}

    def run_all(self, force: bool = False, memories: bool = False) -> dict[str, Any]:
        for table in INGEST_STAGES + (OPTIONAL_STAGES if memories else ()):
            self.run_stage(table, force=force)
        self.run_derived(force=force)
        started = self.conn.execute("SELECT MIN(started_at) FROM sessions").fetchone()[0]
        self.conn.execute(
            "INSERT OR REPLACE INTO meta VALUES ('imported_at', ?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"),),
        )
        self.conn.execute(
            "INSERT OR REPLACE INTO meta VALUES ('limit', ?)", (str(self.limit or ""),)
        )
        self.conn.commit()
        self.progress(f"first session at {started}")
        from report import coverage_report

        return coverage_report(self.conn, self.db_path, self.manifest)


def _on_windows_mount(path: Path) -> bool:
    return str(path).startswith("/mnt/")


def staging_path(final: Path) -> Path:
    cache = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return cache / "trajectory-mining" / final.name


def publish(conn: sqlite3.Connection, work: Path, final: Path) -> None:
    """Fold the WAL into the file, then move the finished index into place."""
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    final.parent.mkdir(parents=True, exist_ok=True)
    partial = final.with_name(final.name + ".partial")
    shutil.copyfile(work, partial)
    partial.replace(final)
    for suffix in ("", "-wal", "-shm"):
        Path(str(work) + suffix).unlink(missing_ok=True)
    print(f"index written to {final}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stream AI Village archives into the index.")
    parser.add_argument("--dir", type=Path, default=Path("../../data/raw"))
    parser.add_argument("--db", type=Path, default=db.DEFAULT_DB_PATH)
    parser.add_argument("--report", action="store_true", help="print the coverage report only")
    parser.add_argument("--force", action="store_true", help="redo stages with a checkpoint")
    parser.add_argument("--rebuild", action="store_true", help="delete this index file first")
    parser.add_argument("--limit", type=int, help="read at most N rows per table (sample run)")
    parser.add_argument("--memories", action="store_true", help="also read agent_memories")
    parser.add_argument("--no-disk-check", action="store_true")
    args = parser.parse_args(argv)

    final = args.db.resolve()
    work = final
    if not args.report and _on_windows_mount(final):
        work = staging_path(final)
        if args.rebuild:
            for target in (work, final):
                for suffix in ("", "-wal", "-shm"):
                    Path(str(target) + suffix).unlink(missing_ok=True)
        if final.exists():
            work = final  # resume or inspect an index that already sits in place
        else:
            work.parent.mkdir(parents=True, exist_ok=True)
            print(
                f"note: SQLite writes on a Windows mount are about 10x slower. Building in {work}, "
                f"then moving the index to {final}.",
                file=sys.stderr,
            )

    try:
        importer = TrajectoryImporter(
            args.dir, work, limit=args.limit, disk_check=not args.no_disk_check,
            rebuild=args.rebuild,
        )
        if args.report:
            from report import coverage_report

            result = coverage_report(importer.conn, importer.db_path, importer.manifest)
        else:
            result = importer.run_all(force=args.force, memories=args.memories)
            if work != final:
                publish(importer.conn, work, final)
    except (db.IndexVersionError, OSError, sqlite3.Error) as err:
        print(f"error: {type(err).__name__}: {err}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
