"""Offline tests for privacy-preserving lexical recurrence discovery."""

import gzip
import json
import tempfile
import unittest
from pathlib import Path

from swarm_forensics.dataset_morphology.discovery import (
    DiscoveryError,
    discover_lexical_recurrence,
)


class LexicalRecurrenceTests(unittest.TestCase):
    def test_cards_reference_repeated_ngrams_without_record_values(self):
        records = [
            {
                "actor": {"id": "actor-private-a"},
                "artifact": {"id": "artifact-private-a"},
                "timestamp": "2025-02-01T12:00:00Z",
                "message": {"body": "Amber signal follows shared state"},
            },
            {
                "actor": {"id": "actor-private-b"},
                "artifact": {"id": "artifact-private-b"},
                "timestamp": "2025-02-02T12:00:00Z",
                "message": {"body": "AMBER SIGNAL follows shared state"},
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "events.jsonl.gz"
            with gzip.open(source, "wt", encoding="utf-8") as handle:
                for record in records:
                    handle.write(json.dumps(record) + "\n")

            report = discover_lexical_recurrence(
                source,
                content_field="/message/body",
                actor_field="/actor/id",
                artifact_field="/artifact/id",
                ngram_size=3,
            )

        self.assertEqual(report["dataset"]["record_count"], 2)
        self.assertEqual(len(report["candidates"]), 3)
        serialized = json.dumps(report, sort_keys=True)
        for secret in (
            "Amber signal follows shared state",
            "actor-private-a",
            "artifact-private-a",
            "2025-02-01T12:00:00Z",
        ):
            self.assertNotIn(secret, serialized)
        for card in report["candidates"]:
            self.assertEqual(card["status"], "weak_lead")
            self.assertEqual(card["evidence_strength"], "e0")
            self.assertEqual(card["distribution"]["unique_records"], 2)
            self.assertEqual(card["distribution"]["distinct_actor_count"], 2)
            self.assertEqual(card["distribution"]["distinct_artifact_count"], 2)
            self.assertEqual(card["first_observed"], None)
            self.assertEqual(card["last_observed"], None)
            self.assertEqual(len(card["evidence"]), 2)
            self.assertTrue(all("#L" in item["source_ref"] for item in card["evidence"]))
            self.assertTrue(all(item["signature_sha256"].startswith("sha256:") for item in card["evidence"]))

    def test_exact_duplicate_records_do_not_inflate_recurrence(self):
        repeated = {"event_id": "event-1", "actor_id": "actor-a", "body": "quiet state handoff"}
        second = {"event_id": "event-2", "actor_id": "actor-b", "body": "quiet state handoff"}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "events.jsonl"
            source.write_text(
                "".join(json.dumps(row) + "\n" for row in (repeated, repeated, second)),
                encoding="utf-8",
            )

            report = discover_lexical_recurrence(
                source,
                content_field="/body",
                actor_field="/actor_id",
                ngram_size=3,
            )

        self.assertEqual(report["dataset"]["record_count"], 3)
        self.assertEqual(report["dataset"]["exact_duplicate_records"], 1)
        self.assertTrue(report["candidates"])
        self.assertTrue(all(card["distribution"]["unique_records"] == 2 for card in report["candidates"]))
        self.assertTrue(all(card["distribution"]["distinct_actor_count"] == 2 for card in report["candidates"]))

    def test_csv_records_stream_and_selectors_must_use_json_pointers(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "events.csv"
            source.write_text(
                "actor_id,body\nactor-a,soft signal received\nactor-b,soft signal received\n",
                encoding="utf-8",
            )

            report = discover_lexical_recurrence(
                source,
                content_field="/body",
                actor_field="/actor_id",
                ngram_size=3,
            )
            with self.assertRaises(DiscoveryError):
                discover_lexical_recurrence(source, content_field="body")

        self.assertEqual(len(report["candidates"]), 1)
        self.assertEqual(report["candidates"][0]["distribution"]["distinct_actor_count"], 2)
        self.assertEqual(
            [item["source_ref"] for item in report["candidates"][0]["evidence"]],
            ["events.csv#L2", "events.csv#L3"],
        )


if __name__ == "__main__":
    unittest.main()
