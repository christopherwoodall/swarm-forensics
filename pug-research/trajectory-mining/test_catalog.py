"""Offline tests: extraction shapes, catalog search, bounded graph slices, evidence labels."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from catalog import (
    HARD_MAX_NODES,
    MAX_ACTIONS_PER_TRACE,
    CatalogError,
    TraceCatalog,
    bucket_plan,
)
from contract import (
    EVIDENCE_CLASSES,
    SCHEMA_VERSION,
    ContractError,
    validate_trajectory_payload,
)
from extract import extract_artifacts, extract_cc_message, extract_turn, read_payload
from importer import TrajectoryImporter
from test_fixtures import A1, A2, A3, generate_synthetic_dataset


class ExtractTests(unittest.TestCase):
    def test_each_provider_shape(self):
        gemini = {"candidates": [{"content": {"parts": [{"text": "g text"}]}}]}
        self.assertEqual(read_payload(gemini, "p")[0:2], ("gemini_candidates", [("p.candidates[0].content.parts[0].text", "g text")]))
        openai_items = [{"type": "message", "content": [{"type": "output_text", "text": "o text"}]}]
        shape, texts, _ = read_payload(openai_items, "p")
        self.assertEqual((shape, texts[0][1]), ("openai_response_items", "o text"))
        anthropic = {"content": [{"type": "text", "text": "a text"}, {"type": "tool_use", "name": "bash", "input": {}}]}
        shape, texts, tools = read_payload(anthropic, "p")
        self.assertEqual((shape, texts[0][1], tools), ("anthropic_blocks", "a text", ["bash"]))
        chat = {"choices": [{"message": {"content": "c text"}}]}
        self.assertEqual(read_payload(chat, "p")[0], "chat_completions")
        self.assertEqual(read_payload("plain", "p")[0], "plain_text")
        self.assertEqual(read_payload(None, "p")[0], "empty")
        self.assertEqual(read_payload({"x": 1}, "p")[0], "unsupported")
        self.assertEqual(read_payload([1, 2], "p")[0], "unsupported")

    def test_every_claim_has_a_field_path(self):
        facts = extract_turn({"agent_action": {"command": "ls"}, "agent_messages": None})
        self.assertEqual(facts.detail_path, "agent_action.command")
        msg = extract_cc_message({"message_type": "assistant", "content": {"message": {"content": [{"type": "text", "text": "hi"}]}}})
        self.assertTrue(msg.text_path.startswith("content.message.content[0]"))

    def test_artifacts_scope_and_limits(self):
        found = extract_artifacts("see https://github.com/o/r.git and /home/x/a.txt", A1)
        self.assertIn(("repo", "o/r", "global"), found)
        self.assertIn(("file", "/home/x/a.txt", f"agent:{A1}"), found)
        self.assertNotIn("file", [k for k, _i, _s in extract_artifacts("/home/x/a.txt", None)])
        many = " ".join(f"https://h{i}.example.org/p" for i in range(100))
        self.assertLessEqual(len(extract_artifacts(many, A1)), 20)
        self.assertFalse([a for a in extract_artifacts("http://127.0.0.1:8000/x http://10.0.0.1/y", A1) if a[0] == "host"])

    def test_unsupported_turn_shape_does_not_crash(self):
        facts = extract_turn({"agent_action": "not a dict", "agent_messages": {"zzz": 1}})
        self.assertEqual((facts.action, facts.shape), ("none", "unsupported"))


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls._tmp.name)
        raw = tmp / "raw"
        generate_synthetic_dataset(raw, big_turns=200)
        cls.imp = TrajectoryImporter(raw, tmp / "i.db", progress=None)
        cls.imp.run_all()
        cls.cat = TraceCatalog(cls.imp.conn)

    @classmethod
    def tearDownClass(cls):
        cls.imp.conn.close()
        cls._tmp.cleanup()

    def graph(self, ids, **kw):
        return self.cat.graph(ids, **kw)

    # -- catalog
    def test_overview_lists_goals_with_unknown_category(self):
        ov = self.cat.overview()
        self.assertEqual(ov["goals"][-1]["id"], "unknown_goal")
        self.assertEqual({a["id"] for a in ov["agents"]}, {A1, A2, A3})
        self.assertEqual(ov["trace_types"]["chat"], 3)
        self.assertEqual(ov["index"]["schema_version"], 2)

    def test_search_filters(self):
        ids = lambda **kw: {t["trace_id"] for t in self.cat.search_traces(**kw)["traces"]}  # noqa: E731
        self.assertEqual(ids(agent_ids=[A1], types=["computer_use"]), {"session:s1", "session:s3"})
        self.assertEqual(ids(goal_id="unknown_goal", types=["computer_use"]), {"session:s4"})
        self.assertEqual(ids(types=["claude_code"]), {"session:cc-1"})
        self.assertEqual(len(ids(types=["chat"])), 3)
        self.assertEqual(ids(date_from="2026-04-24", date_to="2026-04-24", types=["computer_use"]), {"session:s3"})
        self.assertEqual(ids(q="lantern", types=["computer_use"]), {"session:s1"})
        self.assertEqual(ids(agent_ids=[A2], types=["chat"]), {"episode:room-a:0001", "episode:room-a:0002"})

    def test_search_is_paged_and_ordered(self):
        page = self.cat.search_traces(limit=2, offset=0)
        self.assertEqual(len(page["traces"]), 2)
        self.assertGreater(page["total"], 2)
        starts = [t["started_at"] for t in page["traces"]]
        self.assertEqual(starts, sorted(starts, reverse=True))

    def test_bad_parameters_raise_catalog_error_without_values(self):
        with self.assertRaises(CatalogError) as ctx:
            self.cat.search_traces(date_from="2026/01/01")
        self.assertNotIn("2026/01/01", str(ctx.exception))
        with self.assertRaises(CatalogError):
            self.cat.search_traces(types=["bogus"])
        with self.assertRaises(CatalogError):
            self.graph(["session:nope"])
        with self.assertRaises(CatalogError):
            self.graph([f"session:s{i}" for i in range(13)])

    # -- graph
    def test_every_edge_has_class_rule_and_source(self):
        p = self.graph(["session:s1", "session:s3", "session:cc-1", "episode:room-a:0001"])
        self.assertGreater(len(p["edges"]), 10)
        for e in p["edges"]:
            self.assertIn(e["evidence_class"], EVIDENCE_CLASSES)
            self.assertTrue(e["rule"])
            self.assertTrue(e["source_ref"]["table"] and e["source_ref"]["row_id"])
        self.assertEqual(p["schema_version"], SCHEMA_VERSION)
        self.assertEqual(set(p["meta"]["evidence_classes"]), {"recorded", "rule_derived"})

    def test_four_tiers_and_goal_tier_is_intention_only(self):
        p = self.graph(["session:s1", "session:s3"])
        self.assertEqual(set(p["meta"]["tiers"]), {"agent", "action", "artifact", "goal"})
        text = json.dumps(p).lower()
        for word in ("achieved", "completed the goal", "succeeded"):
            self.assertNotIn(word, text)
        temporal = [e for e in p["edges"] if e["rule"].startswith("temporal_window")]
        self.assertTrue(temporal)
        self.assertTrue(all(e["label"] == "temporal_context" and e["evidence_class"] == "rule_derived" for e in temporal))
        intents = [n for n in p["nodes"] if n["id"].startswith("intent:")]
        self.assertTrue(all(n["claims"][0]["field_path"] == "session_goal" for n in intents))

    def test_unknown_goal_and_gaps_are_visible(self):
        p = self.graph(["session:s4", "session:s2"])
        self.assertIn("goal:unknown_goal", {n["id"] for n in p["nodes"]})
        kinds = {g["kind"] for g in p["meta"]["gaps"]}
        self.assertIn("session_goal_missing", kinds)
        self.assertIn("session_without_items", kinds)

    def test_boundary_session_links_to_each_overlapping_goal(self):
        p = self.graph(["session:s3"])
        rules = {e["rule"] for e in p["edges"] if e["label"] == "temporal_context"}
        self.assertIn("temporal_window:crosses_end", rules)
        self.assertIn("temporal_window:within", rules)

    def test_large_trace_is_aggregated_and_reported(self):
        p = self.graph(["session:s-big"])
        self.assertEqual(len(p["meta"]["aggregation"]), 1)
        agg = p["meta"]["aggregation"][0]
        self.assertEqual(agg["items"], 200)
        self.assertLessEqual(agg["nodes"], MAX_ACTIONS_PER_TRACE)
        runs = [n for n in p["nodes"] if n["id"].startswith("run:")]
        self.assertEqual(len(runs), agg["nodes"])
        self.assertEqual(sum(n["metadata"]["items"] for n in runs), 200)
        self.assertTrue(all(e["evidence_class"] == "rule_derived" for e in p["edges"] if e["target"].startswith("run:")))
        self.assertTrue(p["meta"]["is_bounded"])
        self.assertEqual(bucket_plan(200, 40), (5, 40))
        self.assertEqual(bucket_plan(7, 40), (1, 7))

    def test_small_trace_has_one_node_per_turn_with_recorded_edges(self):
        p = self.graph(["session:s1"])
        turns = [n for n in p["nodes"] if n["id"].startswith("turn:")]
        self.assertEqual(len(turns), 3)
        edges = [e for e in p["edges"] if e["target"].startswith("turn:")]
        self.assertTrue(all(e["evidence_class"] == "recorded" for e in edges))
        self.assertFalse(p["meta"]["aggregation"])

    def test_node_budget_is_hard(self):
        p = self.graph(["session:s1", "session:s3", "session:cc-1", "session:s-big"], max_nodes=20)
        self.assertLessEqual(len(p["nodes"]), 20)
        self.assertTrue(p["meta"]["hidden"] or p["meta"]["aggregation"])
        ids = {n["id"] for n in p["nodes"]}
        self.assertTrue(all(e["source"] in ids and e["target"] in ids for e in p["edges"]))
        big = self.graph(["session:s1"], max_nodes=10**9)
        self.assertEqual(big["meta"]["max_nodes"], HARD_MAX_NODES)

    def test_files_stay_scoped_to_agent_across_traces(self):
        p = self.graph(["session:s1", "session:s2"])
        files = [n for n in p["nodes"] if n["metadata"].get("artifact_kind") == "file"]
        self.assertEqual({n["metadata"]["scope"] for n in files}, {f"agent:{A1}", f"agent:{A2}"})
        self.assertEqual(len({n["id"] for n in files}), 2)

    def test_shared_url_and_language_carry_non_proof_notes(self):
        p = self.graph(["session:s1", "session:cc-1"])
        shared = [n for n in p["nodes"] if n["metadata"].get("selected_traces", 0) > 1]
        self.assertTrue(shared)
        self.assertTrue(all("does not show coordination" in n["metadata"]["note"] for n in shared))
        lang = [e for e in p["edges"] if e["rule"] == "shared_rare_language"]
        self.assertTrue(lang)
        self.assertTrue(all("not show collaboration" in e["note"] for e in lang))

    def test_chat_episode_graph(self):
        p = self.graph(["episode:room-a:0001"])
        self.assertEqual({n["id"] for n in p["nodes"] if n["tier"] == "agent"}, {f"agent:{A1}", f"agent:{A2}"})
        msgs = [n for n in p["nodes"] if n["id"].startswith("message:")]
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0]["claims"][0]["field_path"], "content")

    def test_timeline_is_ordered_and_numbered(self):
        p = self.graph(["session:s1"])
        ats = [t["at"] for t in p["timeline"]]
        self.assertEqual(ats, sorted(ats))
        self.assertEqual([t["seq"] for t in p["timeline"]], list(range(len(ats))))

    def test_output_is_deterministic(self):
        ids = ["session:s1", "session:s3", "episode:room-a:0001"]
        a = json.dumps(self.graph(ids), sort_keys=True)
        b = json.dumps(self.graph(ids), sort_keys=True)
        self.assertEqual(a, b)

    def test_validator_rejects_bad_payloads_without_values(self):
        secret = "do-not-leak-this"
        bad = {"schema_version": 2, "nodes": [{"id": "n", "tier": "bad", "label": secret,
                                                "source_ref": {"table": "t", "row_id": 1}}], "edges": []}
        with self.assertRaises(ContractError) as ctx:
            validate_trajectory_payload(bad)
        self.assertNotIn(secret, str(ctx.exception))
        node = {"id": "n", "tier": "agent", "label": "x", "source_ref": {"table": "t", "row_id": 1}}
        edge = {"source": "n", "target": "n", "evidence_class": "recorded", "rule": "r",
                "source_ref": {"table": "t", "row_id": 1}, "label": "achieved"}
        with self.assertRaises(ContractError):
            validate_trajectory_payload({"schema_version": 2, "nodes": [node], "edges": [edge]})
        edge.update(label="ok", evidence_class="guess")
        with self.assertRaises(ContractError):
            validate_trajectory_payload({"schema_version": 2, "nodes": [node], "edges": [edge]})

    # -- playback
    def test_steps_page_and_map_to_nodes(self):
        small = self.cat.steps("session:s1")
        self.assertEqual([s["seq"] for s in small["steps"]], [0, 1, 2])
        self.assertTrue(all(s["node_id"].startswith("turn:") for s in small["steps"]))
        big = self.cat.steps("session:s-big", offset=0, limit=10)
        self.assertEqual(big["total"], 200)
        self.assertEqual(big["bucket_size"], 5)
        self.assertEqual({s["node_id"] for s in big["steps"]}, {"run:s-big:0", "run:s-big:1"})
        graph_ids = {n["id"] for n in self.graph(["session:s-big"])["nodes"]}
        self.assertTrue({s["node_id"] for s in big["steps"]} <= graph_ids)
        with self.assertRaises(CatalogError):
            self.cat.steps("session:missing")

    def test_inferred_edges_only_appear_when_stored(self):
        conn = self.imp.conn
        conn.execute(
            "INSERT INTO llm_runs (created_at, provider, model, max_usd, spent_usd, calls, status) "
            "VALUES ('t', 'openai', 'm', 1, 0, 1, 'ok')"
        )
        conn.execute(
            "INSERT INTO llm_links (run_id, source_node, target_node, relation, rationale, cited_ids) "
            "VALUES (1, 'session:s1', 'session:s3', 'similar_topic', 'Both mention notes.', '[]')"
        )
        conn.commit()
        try:
            with_llm = self.graph(["session:s1", "session:s3"])
            classes = {e["evidence_class"] for e in with_llm["edges"]}
            self.assertIn("inferred", classes)
            without = self.graph(["session:s1", "session:s3"], include_inferred=False)
            self.assertNotIn("inferred", {e["evidence_class"] for e in without["edges"]})
        finally:
            conn.execute("DELETE FROM llm_links")
            conn.execute("DELETE FROM llm_runs")
            conn.commit()


if __name__ == "__main__":
    unittest.main()
