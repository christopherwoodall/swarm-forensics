"""Offline tests: importer, joins, goals, episodes, language, redaction, reports."""

from __future__ import annotations

import gzip
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import db
import goals
from contract import ContractError, parse_utc_timestamp, sanitize_text
from episodes import EPISODE_GAP_MINUTES
from importer import Reader, TrajectoryImporter, norm_ts
from language import MAX_OWNERS_PER_TERM, extract_language
from test_fixtures import A1, A2, EMAIL, SECRET, generate_synthetic_dataset, write_gz_jsonl


def build(tmp: Path, name: str = "x", **kwargs) -> tuple[TrajectoryImporter, dict, dict]:
    raw = tmp / f"raw-{name}"
    counts = generate_synthetic_dataset(raw, **kwargs.pop("fixture", {}))
    imp = TrajectoryImporter(raw, tmp / f"{name}.db", progress=None, **kwargs)
    return imp, imp.run_all(), counts


class ImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.imp, cls.report, cls.counts = build(cls.tmp)
        cls.c = cls.imp.conn

    @classmethod
    def tearDownClass(cls):
        cls.c.close()
        cls._tmp.cleanup()

    def q(self, sql, *args):
        return [tuple(r) for r in self.c.execute(sql, args)]

    # -- counts and reports
    def test_rows_read_match_manifest_and_report_gap(self):
        for table, n in self.counts.items():
            entry = self.report["tables"][table]
            self.assertEqual(entry["rows_read"], n, table)
            self.assertEqual(entry["manifest_gap"], 0, table)
        turns = self.report["tables"]["computer_use_turns"]
        self.assertEqual((turns["rows_indexed"], turns["rows_skipped"]), (7, 1))
        self.assertEqual(turns["reasons"]["missing_session_id"], 1)

    def test_orphans_and_gaps_reported(self):
        o = self.report["orphans_and_gaps"]
        self.assertEqual(o["turns_without_session"], 1)
        self.assertEqual(o["sessions_without_agent"], 1)
        self.assertEqual(o["messages_without_session"], 1)
        self.assertEqual(o["computer_use_sessions_without_turns"], 3)
        self.assertEqual(o["computer_use_sessions_without_session_goal"], 2)
        self.assertEqual(self.report["agents"]["agents_with_agent_goal_rows"], 1)

    def test_unsupported_shapes_reported_without_values(self):
        shapes = {(u["table"], u["shape"]): u["rows"] for u in self.report["unsupported_shapes"]}
        self.assertEqual(shapes[("computer_use_turns", "agent_messages:unsupported")], 1)
        self.assertEqual(shapes[("claude_code_messages", "content:unsupported")], 1)
        self.assertNotIn("weird", json.dumps(self.report))

    def test_all_provider_shapes_read(self):
        got = set(self.report["supported_shapes"]["computer_use_turns"])
        self.assertEqual(
            got,
            {f"agent_messages:{s}" for s in (
                "gemini_candidates", "openai_response_items", "anthropic_blocks",
                "chat_completions", "empty")},
        )  # fmt: skip

    # -- sessions and goals
    def test_null_and_blank_session_goal_kept_as_null(self):
        rows = dict(self.q("SELECT id, goal_text FROM sessions WHERE id IN ('s2','s4')"))
        self.assertEqual(rows, {"s2": None, "s4": None})
        self.assertEqual(self.q("SELECT COUNT(*) FROM sessions WHERE id = 's4'")[0][0], 1)

    def test_session_window_uses_last_turn(self):
        (end,) = self.q("SELECT window_end FROM sessions WHERE id = 's3'")[0]
        self.assertEqual(end, "2026-04-25 02:00:00.000000")

    def test_boundary_crossing_links_both_goals(self):
        got = dict(self.q("SELECT goal_id, overlap FROM goal_links WHERE owner_id = 'session:s3'"))
        self.assertEqual(got["vg-1"], "crosses_end")
        self.assertEqual(got["vg-2"], "within")
        self.assertIn("ag-1", got)

    def test_overlapping_goals_and_unknown_goal(self):
        s1 = {r[0] for r in self.q("SELECT goal_id FROM goal_links WHERE owner_id = 'session:s1'")}
        self.assertEqual(s1, {"vg-1", "ag-1"})
        s4 = self.q("SELECT goal_id, overlap FROM goal_links WHERE owner_id = 'session:s4'")
        self.assertEqual(s4, [("unknown_goal", "none")])

    def test_agent_goal_applies_to_its_agent_only(self):
        links = self.q("SELECT owner_id FROM goal_links WHERE goal_id = 'ag-1'")
        self.assertTrue(all(o in ("session:s1", "session:s3") for (o,) in links))

    def test_open_ended_goal_ends_at_next_start(self):
        conn = sqlite3.connect(":memory:")
        conn.executescript(db.TABLES_DDL)
        rows = [
            ("g1", "agent", "a", "x", None, "2026-01-01 00:00:00.000000", None, None, "t", 1),
            ("g2", "agent", "a", "x", None, "2026-02-01 00:00:00.000000", None, None, "t", 2),
            ("g3", "village", None, "x", None, None, None, None, "t", 3),
        ]
        conn.executemany("INSERT INTO goals VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
        stats = goals.resolve_windows(conn)
        ends = dict(conn.execute("SELECT id, effective_end FROM goals"))
        self.assertEqual(ends["g1"], "2026-02-01 00:00:00.000000")
        self.assertIsNone(ends["g2"])
        self.assertEqual(stats["goals_without_start"], 1)

    def test_overlap_kind_function_matches_rules(self):
        a, b = "2026-01-10", "2026-01-20"
        self.assertEqual(goals.overlap_kind("2026-01-11", "2026-01-12", a, b), "within")
        self.assertEqual(goals.overlap_kind("2026-01-05", "2026-01-12", a, b), "crosses_start")
        self.assertEqual(goals.overlap_kind("2026-01-15", "2026-01-25", a, b), "crosses_end")
        self.assertEqual(goals.overlap_kind("2026-01-05", "2026-01-25", a, b), "spans")
        self.assertEqual(goals.overlap_kind("2026-02-01", "2026-02-02", a, b), "none")
        self.assertEqual(goals.overlap_kind("2026-02-01", "2026-02-02", a, None), "within")

    # -- chat and events
    def test_mirrored_chat_events_are_flagged_not_duplicated(self):
        flags = dict(self.q("SELECT id, mirrored FROM events WHERE message_id IS NOT NULL"))
        self.assertEqual(flags, {"e1": 1, "e2": 0, "e6": 1})
        chat = self.q("SELECT COUNT(*) FROM messages WHERE source_table = 'chat_messages'")[0][0]
        self.assertEqual(chat, 6)
        self.assertEqual(self.report["chat"]["talk_events_mirrored_in_chat"], 2)
        self.assertEqual(self.report["chat"]["talk_events_without_chat_row"], 1)

    def test_event_order_is_index_then_time_then_id(self):
        order = [
            r[0] for r in self.q(
                "SELECT id FROM events ORDER BY event_index, created_at, id"
            )
        ]  # fmt: skip
        self.assertEqual(order, ["e1", "e2", "e3", "e4", "e5", "e6"])

    def test_events_join_session_by_computer_use_session_id(self):
        (ref,) = self.q("SELECT session_ref FROM events WHERE id = 'e3'")[0]
        self.assertEqual(ref, "s1")

    def test_episodes_split_on_gap(self):
        eps = self.q("SELECT id, message_count, agent_count FROM episodes ORDER BY id")
        self.assertEqual(eps, [("room-a:0001", 3, 2), ("room-a:0002", 2, 2), ("room-b:0001", 1, 1)])
        self.assertEqual(EPISODE_GAP_MINUTES, 30)
        users = self.q("SELECT agent_id FROM episode_members WHERE agent_id LIKE 'user:%'")
        self.assertEqual(users, [("user:human-1",)])

    def test_claude_code_messages_join_by_sdk_session_id(self):
        rows = dict(self.q("SELECT id, session_id FROM messages WHERE source_table = 'claude_code_messages'"))
        self.assertEqual(rows["m1"], "cc-1")
        self.assertIsNone(rows["m4"])
        self.assertEqual(self.q("SELECT item_count FROM sessions WHERE id = 'cc-1'")[0][0], 4)

    # -- artifacts and language
    def test_file_paths_are_scoped_by_agent(self):
        scopes = {
            r[0] for r in self.q(
                "SELECT scope FROM artifacts WHERE kind = 'file' "
                "AND identifier = '/home/computeruse/work/notes.txt'"
            )
        }  # fmt: skip
        self.assertEqual(scopes, {f"agent:{A1}", f"agent:{A2}"})

    def test_repo_name_keeps_trailing_letters(self):
        repos = {r[0] for r in self.q("SELECT identifier FROM artifacts WHERE kind = 'repo'")}
        self.assertEqual(repos, {"pug/core"})

    def test_document_title_and_google_doc_artifacts(self):
        self.assertTrue(self.q("SELECT 1 FROM artifacts WHERE kind = 'title' AND identifier = 'Protocol notes'"))
        self.assertTrue(self.q("SELECT 1 FROM artifacts WHERE kind = 'document'"))

    def test_shared_language_needs_two_agents(self):
        owners = {r[0] for r in self.q("SELECT owner_id FROM language_links WHERE term = 'lantern protocol'")}
        self.assertEqual(owners, {"session:s1", "session:cc-1", "episode:room-a:0001"})
        self.assertFalse(self.q("SELECT 1 FROM language_links WHERE term = 'xylophonic'"))
        rows = self.q("SELECT n_agents, score FROM language_links WHERE term = 'lantern protocol'")
        self.assertTrue(all(n == 2 and abs(s - 0.3333) < 1e-4 for n, s in rows))

    def test_language_cap_per_term(self):
        conn = sqlite3.connect(":memory:")
        conn.executescript(db.TABLES_DDL)
        for i in range(MAX_OWNERS_PER_TERM + 1):
            conn.execute(
                "INSERT INTO sessions (id, kind, agent_id, goal_text, source_table, line) "
                "VALUES (?, 'computer_use', ?, 'the zeppelin plan', 'computer_use_sessions', ?)",
                (f"s{i}", f"a{i}", i),
            )
        from language import build_language_links

        stats = build_language_links(conn)
        self.assertEqual(stats["links"], 0)
        conn.execute("DELETE FROM sessions WHERE id = 's0'")
        self.assertEqual(build_language_links(conn)["links"], MAX_OWNERS_PER_TERM)

    def test_extract_language_ignores_urls_and_paths(self):
        phrases, terms = extract_language('see https://example.org/zeppelinaut and /tmp/zeppelinfile')
        self.assertFalse(terms & {"zeppelinaut", "zeppelinfile"})
        phrases, terms = extract_language('He said "the blue lantern" twice')
        self.assertEqual(phrases, {"the blue lantern"})

    # -- redaction
    def test_secrets_never_reach_the_index(self):
        dump = "\n".join(self.c.iterdump())
        self.assertNotIn(SECRET, dump)
        self.assertNotIn(EMAIL, dump)
        (out,) = self.q("SELECT output FROM turns WHERE id = 't1'")[0]
        self.assertIn("[MASKED]", out)

    def test_typed_text_is_not_stored(self):
        (detail,) = self.q("SELECT detail FROM turns WHERE id = 't6'")[0]
        self.assertIsNone(detail)
        self.assertTrue(self.q("SELECT 1 FROM artifacts WHERE kind = 'host' AND identifier = 'example.org'"))

    def test_text_is_bounded(self):
        self.assertLessEqual(len(sanitize_text("x" * 5000, 100)), 140)

    def test_sanitize_masks_each_class_and_skips_clean_text(self):
        cases = {
            "Authorization: Bearer abcdefgh12345678": "Bearer [MASKED]",
            "key hf_abcdefghij1234": "[MASKED]",
            "API_KEY=supersecret": "API_KEY=[MASKED]",
            "mail bob@example.com now": "[EMAIL]",
            "host 10.1.2.3 up": "[IP]",
        }
        for text, expected in cases.items():
            self.assertIn(expected, sanitize_text(text), text)
        self.assertEqual(sanitize_text("plain text, version 1.2"), "plain text, version 1.2")
        self.assertEqual(sanitize_text(None), "")

    # -- determinism and idempotence
    def test_two_builds_are_identical(self):
        imp2, _, _ = build(self.tmp, "second")
        for table in ("sessions", "turns", "messages", "events", "artifacts", "goal_links",
                      "language_links", "episodes", "episode_members"):  # fmt: skip
            a = self.q(f"SELECT * FROM {table} ORDER BY 1, 2, 3")
            b = [tuple(r) for r in imp2.conn.execute(f"SELECT * FROM {table} ORDER BY 1, 2, 3")]
            self.assertEqual(a, b, table)
        imp2.conn.close()

    def test_rerun_skips_complete_stages_and_keeps_rows(self):
        before = self.q("SELECT COUNT(*) FROM turns")[0][0]
        again = TrajectoryImporter(self.imp.data_dir, self.imp.db_path, progress=None)
        self.assertEqual(again.run_stage("computer_use_turns"), "skipped")
        again.run_all()
        self.assertEqual([], again.ran)
        self.assertEqual(self.q("SELECT COUNT(*) FROM turns")[0][0], before)
        self.assertEqual(again.run_stage("computer_use_turns", force=True), "complete")
        self.assertEqual(self.q("SELECT COUNT(*) FROM turns")[0][0], before)
        again.conn.close()

    def test_timestamps_normalize(self):
        self.assertEqual(norm_ts("2026-03-18 20:40:06.5"), "2026-03-18 20:40:06.500000")
        self.assertEqual(norm_ts("2026-03-18T20:40:06Z"), "2026-03-18 20:40:06.000000")
        self.assertIsNone(norm_ts("not a time"))
        self.assertIsNone(norm_ts(None))
        self.assertEqual(parse_utc_timestamp("2026-03-18 20:40:06.5").microsecond, 500000)
        with self.assertRaises(ContractError):
            parse_utc_timestamp("bad")


class DamagedInputTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_malformed_json_damaged_gzip_and_missing_tables(self):
        raw = self.tmp / "raw"
        raw.mkdir()
        (raw / "agents.jsonl.gz").write_bytes(b"not gzip at all")
        write_gz_jsonl(
            raw / "computer_use_sessions.jsonl.gz",
            [{"id": "s1", "agent_id": "a", "created_at": "2026-01-01 00:00:00"}, {"agent_id": "x"}],
            ["{not json SECRETVALUE", "[1, 2]"],
        )
        imp = TrajectoryImporter(raw, self.tmp / "i.db", progress=None)
        report = imp.run_all()
        agents = report["tables"]["agents"]
        self.assertEqual(agents["status"], "partial")
        self.assertEqual(agents["reasons"]["damaged_gzip"], 1)
        sessions = report["tables"]["computer_use_sessions"]
        self.assertEqual(sessions["status"], "complete")
        self.assertEqual(sessions["rows_indexed"], 1)
        self.assertEqual(
            (sessions["reasons"]["bad_json"], sessions["reasons"]["not_object"],
             sessions["reasons"]["missing_id"]),
            (1, 1, 1),
        )  # fmt: skip
        self.assertEqual(report["tables"]["events"]["status"], "missing")
        self.assertIn("events", [k for k in report["tables"] if report["tables"][k]["status"] == "missing"])
        self.assertNotIn("SECRETVALUE", json.dumps(report))
        imp.conn.close()

    def test_truncated_gzip_keeps_rows_before_damage(self):
        raw = self.tmp / "raw"
        raw.mkdir()
        path = raw / "agents.jsonl.gz"
        rows = "".join(json.dumps({"id": f"a{i}", "name": "n" * 50}) + "\n" for i in range(2000))
        data = gzip.compress(rows.encode())
        path.write_bytes(data[: len(data) // 2])
        reader = Reader(path)
        got = list(reader)
        self.assertTrue(reader.damaged)
        self.assertGreater(len(got), 0)

    def test_missing_files_are_reported_not_fatal(self):
        raw = self.tmp / "empty"
        raw.mkdir()
        imp = TrajectoryImporter(raw, self.tmp / "e.db", progress=None)
        report = imp.run_all()
        self.assertTrue(all(t["status"] == "missing" for k, t in report["tables"].items() if not k.startswith("derived")))
        self.assertEqual(report["orphans_and_gaps"]["turns_without_session"], 0)
        imp.conn.close()

    def test_sample_limit_marks_the_index(self):
        raw = self.tmp / "raw"
        generate_synthetic_dataset(raw)
        imp = TrajectoryImporter(raw, self.tmp / "l.db", limit=2, progress=None)
        report = imp.run_all()
        self.assertEqual(report["sample_limit"], "2")
        self.assertEqual(report["tables"]["computer_use_turns"]["rows_read"], 2)
        imp.conn.close()

    def test_version_mismatch_is_refused_and_rebuild_recovers(self):
        path = self.tmp / "old.db"
        old = sqlite3.connect(path)
        old.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
        old.execute("INSERT INTO meta VALUES ('schema_version', '1')")
        old.commit()
        old.close()
        with self.assertRaises(db.IndexVersionError) as ctx:
            db.connect(path)
        self.assertIn("schema version 1", str(ctx.exception))
        raw = self.tmp / "raw"
        generate_synthetic_dataset(raw)
        imp = TrajectoryImporter(raw, path, progress=None, rebuild=True)
        self.assertEqual(imp.run_all()["schema_version"], 2)
        imp.conn.close()

    def test_diagnostics_hold_no_record_values(self):
        with self.assertRaises(ContractError) as ctx:
            parse_utc_timestamp("secret-looking-value")
        self.assertNotIn("secret", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
