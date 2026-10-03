"""Offline tests for the stage-4 traces subsystem. No network, no raw archives."""

import json
import unittest

from swarm_forensics.traces.readers import technique_family_for
from swarm_forensics.traces.rows import actor_hint_for_label, added_text, mk_edge, mk_event
from swarm_forensics.traces.schema import (
    validate_edge,
    validate_event,
)


class SchemaTests(unittest.TestCase):
    def test_valid_event_passes(self):
        row = mk_event(
            eid="e-1",
            dataset="wiki",
            time="2026-05-26T16:43:26Z",
            actor_hint="investigator",
            action="write",
            target="wiki:dse~TestAgentResearchLinks",
            artifact="page:dse~TestAgentResearchLinks",
            operation="save",
            technique_family="wiki_write",
            raw_ref="full-wiki-logs.zip!revisions.jsonl:dse~TestAgentResearchLinks@1",
        )
        self.assertEqual(validate_event(row), [])

    def test_invalid_dataset_and_action_are_caught(self):
        row = mk_event(
            eid="e-2",
            dataset="twitter",
            time="",
            actor_hint="unattributed",
            action="delete",
            target="t",
            artifact="a",
            operation="op",
            technique_family="unknown",
            raw_ref="ref",
        )
        problems = validate_event(row)
        self.assertTrue(any("dataset" in p for p in problems))
        self.assertTrue(any("action" in p for p in problems))

    def test_invalid_strength_is_caught(self):
        edge = mk_edge(
            eid="x-1",
            edge_from="a",
            edge_to="b",
            relation="r",
            evidence_type="t",
            causal_strength="definitely_caused",
            competing="c",
            raw_ref="ref",
        )
        problems = validate_edge(edge)
        self.assertEqual(len(problems), 1)
        self.assertIn("causal_strength", problems[0])

    def test_actor_hint_enum_is_enforced(self):
        row = mk_event(
            eid="e-3",
            dataset="wiki",
            time="t",
            actor_hint="robot",
            action="write",
            target="t",
            artifact="a",
            technique_family="wiki_write",
            operation="save",
            raw_ref="ref",
        )
        problems = validate_event(row)
        self.assertTrue(any("actor_hint" in p for p in problems))


class ReaderTests(unittest.TestCase):
    def test_relay_and_shortener_classification(self):
        self.assertEqual(technique_family_for("https://markdown.new/https://x.gov/a"), "relay_fetch")
        self.assertEqual(technique_family_for("http://httpbin.org/redirect-to?url=x"), "relay_indirection")
        self.assertEqual(technique_family_for("https://is.gd/abc"), "shortener_c2")
        self.assertEqual(technique_family_for("https://plain.example.gov/data"), "unknown")

    def test_investigator_label_maps_to_investigator_hint(self):
        self.assertEqual(actor_hint_for_label("ResearchUser"), "investigator")
        self.assertEqual(actor_hint_for_label("AgentOurGroceryGeorgiaLinkY"), "agent_label")
        self.assertEqual(actor_hint_for_label(""), "unattributed")

    def test_added_text_reconstruction(self):
        rev = {
            "body": "keep\nnew-a\nnew-b\nkeep2",
            "hunks": [
                {"op": "insert", "a0": 1, "a1": 1, "b0": 1, "b1": 3},
                {"op": "context", "a0": 0, "a1": 1, "b0": 0, "b1": 1},
            ],
        }
        self.assertEqual(added_text(rev), "new-a\nnew-b")


class VizTests(unittest.TestCase):
    def test_build_summary_counts_and_stems(self):
        import tempfile
        from pathlib import Path

        from swarm_forensics.traces.viz import build_summary

        events = [
            {"dataset": "arquivo", "time": "2026-06-17T00:02:20Z", "action": "request",
             "actor_hint": "unattributed", "technique_family": "nonce_grammar",
             "target": "https://x.example/api?zz=hf889", "notes": "zz_nonce=hf889"},
            {"dataset": "arquivo", "time": "2026-06-17T01:02:20Z", "action": "request",
             "actor_hint": "unattributed", "technique_family": "unknown",
             "target": "https://x.example/api", "notes": ""},
            {"dataset": "rubygems", "time": "2026-06-01T00:00:00Z", "action": "register",
             "actor_hint": "unattributed", "technique_family": "registry_abuse",
             "target": "rubygems:amdvar123456", "notes": ""},
            {"dataset": "wiki", "time": "2026-05-26T16:43:26Z", "action": "write",
             "actor_hint": "investigator", "technique_family": "wiki_write",
             "target": "wiki:dse~TestAgentResearchLinks", "notes": ""},
        ]
        edges = [{"edge_id": "e1", "causal_strength": "resemblance_only"}]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            events_path = tmp_path / "events.jsonl"
            edges_path = tmp_path / "edges.jsonl"
            with open(events_path, "w") as handle:
                handle.writelines(json.dumps(row) + "\n" for row in events)
            with open(edges_path, "w") as handle:
                handle.write(json.dumps(edges[0]) + "\n")
            summary = build_summary(events_path, edges_path)
        self.assertEqual(summary["totals"]["events"], 4)
        self.assertEqual(summary["totals"]["edges"], 1)
        self.assertEqual(summary["totals"]["by_dataset"]["arquivo"], 2)
        self.assertEqual(summary["gem_stems"], [("amdvar", 1)])
        self.assertEqual(summary["zz_nonces"], [("hf889", 1)])
        self.assertIn("wiki", summary["time_bounds"])


if __name__ == "__main__":
    unittest.main()
