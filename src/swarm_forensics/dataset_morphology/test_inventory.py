"""Offline tests for generic dataset reconnaissance. Fixtures are synthetic."""

import gzip
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from swarm_forensics.dataset_morphology.inventory import (
    InventoryError,
    inventory_dataset,
    main,
)


class JsonlInventoryTests(unittest.TestCase):
    def test_gzip_jsonl_reports_fields_duplicates_and_timestamp_quality(self):
        records = [
            {
                "event_id": "event-1",
                "actor_id": "actor-1",
                "timestamp": "2025-01-01T12:00:00Z",
                "message": {"content": "synthetic private text"},
                "state": {"status": "ready"},
            },
            {
                "event_id": "event-1",
                "actor_id": "actor-1",
                "timestamp": "2025-01-01T12:00:00Z",
                "message": {"content": "synthetic private text"},
                "state": {"status": "ready"},
            },
            {
                "event_id": "event-2",
                "actor_id": None,
                "timestamp": "not-a-date",
                "message": {"content": "another synthetic phrase"},
                "state": {"status": "done"},
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                for record in records:
                    handle.write(json.dumps(record) + "\n")

            report = inventory_dataset(path)

        fields = {field["path"]: field for field in report["fields"]}
        actor = next(item for item in report["candidate_fields"] if item["path"] == "/actor_id")
        timestamp = next(item for item in report["timestamps"] if item["path"] == "/timestamp")
        self.assertEqual(report["dataset"]["record_count"], 3)
        self.assertEqual(fields["/message/content"]["present_records"], 3)
        self.assertEqual(fields["/actor_id"]["null_records"], 1)
        self.assertEqual(actor["kind"], "actor_identifier")
        self.assertEqual(actor["distinct_non_null_values"], 1)
        self.assertEqual(timestamp["parseable_records"], 2)
        self.assertEqual(timestamp["invalid_records"], 1)
        self.assertEqual(report["duplicates"]["exact_duplicate_records"], 1)
        self.assertNotIn("synthetic private text", json.dumps(report))

    def test_json_pointer_paths_escape_field_names(self):
        record = {"a/b": {"~id": "value"}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")

            report = inventory_dataset(path)

        self.assertIn("/a~1b", {field["path"] for field in report["fields"]})
        self.assertIn("/a~1b/~0id", {field["path"] for field in report["fields"]})

    def test_nested_actor_and_message_identifiers_are_candidates(self):
        record = {"actor": {"id": "actor-1"}, "message_id": "message-1"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")

            report = inventory_dataset(path)

        candidates = {item["path"]: item["kind"] for item in report["candidate_fields"]}
        self.assertEqual(candidates["/actor/id"], "actor_identifier")
        self.assertEqual(candidates["/message_id"], "artifact_identifier")

    def test_candidate_fields_report_missing_records(self):
        records = [{"actor_id": "actor-1"}, {"event_id": "event-2"}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")

            report = inventory_dataset(path)

        actor = next(item for item in report["candidate_fields"] if item["path"] == "/actor_id")
        self.assertEqual(actor["present_records"], 1)
        self.assertEqual(actor["missing_records"], 1)


class FormatInventoryTests(unittest.TestCase):
    def test_ndjson_source_format_is_reported_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.ndjson"
            path.write_text('{"event_type":"write"}\n', encoding="utf-8")

            report = inventory_dataset(path)

        self.assertEqual(report["dataset"]["format_file_counts"], {"ndjson": 1})
        self.assertEqual(report["sources"][0]["format"], "ndjson")

    def test_directory_scan_reads_gzip_csv_and_counts_ignored_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "nested" / "messages.csv.gz"
            source.parent.mkdir()
            with gzip.open(source, "wt", encoding="utf-8", newline="") as handle:
                handle.write("actor_id,created_at,content\n")
                handle.write("actor-1,2025-01-01T00:00:00Z,synthetic text\n")
                handle.write("actor-2,,\n")
            (root / "image.png").write_bytes(b"not read")

            report = inventory_dataset(root)

        fields = {field["path"]: field for field in report["fields"]}
        actor = next(item for item in report["candidate_fields"] if item["path"] == "/actor_id")
        self.assertEqual(report["dataset"]["record_count"], 2)
        self.assertEqual(report["dataset"]["format_file_counts"], {"csv": 1})
        self.assertEqual(report["input"]["ignored_file_count"], 1)
        self.assertEqual(report["input"]["ignored_extensions"], {".png": 1})
        self.assertEqual(fields["/created_at"]["empty_string_records"], 1)
        self.assertEqual(actor["distinct_non_null_values"], 2)
        self.assertNotIn("synthetic text", json.dumps(report))

    def test_unsupported_input_fails_with_a_safe_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "secret-image.png"
            path.write_bytes(b"synthetic")
            with self.assertRaises(InventoryError) as context:
                inventory_dataset(path)

        self.assertIn("unsupported file format", str(context.exception))
        self.assertNotIn("synthetic", str(context.exception))

    def test_timestamp_quality_separates_aware_naive_and_epoch_values(self):
        records = [
            {"timestamp": "2025-01-01T00:00:00Z", "event_type": "write", "state": "ready"},
            {"timestamp": 1735689600000, "event_type": "read", "state": "done"},
            {"timestamp": "2025-01-02 00:00:00", "event_type": "write", "state": "ready"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")

            report = inventory_dataset(path)

        timestamp = report["timestamps"][0]
        self.assertEqual(timestamp["parseable_records"], 3)
        self.assertEqual(timestamp["timezone_aware_records"], 2)
        self.assertEqual(timestamp["timezone_naive_records"], 1)
        self.assertEqual(timestamp["formats"]["epoch_milliseconds"], 1)
        self.assertEqual(report["unit_assessment"]["hypothesis"], "mixed_signals")
        self.assertIn("Field names only", report["unit_assessment"]["basis"])

    def test_malformed_json_error_does_not_expose_record_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text('{"content":"private-synthetic-value"\n', encoding="utf-8")
            with self.assertRaises(InventoryError) as context:
                inventory_dataset(path)

        self.assertIn("malformed JSON", str(context.exception))
        self.assertNotIn("private-synthetic-value", str(context.exception))

    def test_cli_reports_input_errors_without_record_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.jsonl"
            path.write_text('{"content":"private-synthetic-value"\n', encoding="utf-8")
            errors = StringIO()
            with redirect_stderr(errors):
                result = main([str(path)])

        self.assertEqual(result, 1)
        self.assertIn("malformed JSON", errors.getvalue())
        self.assertNotIn("private-synthetic-value", errors.getvalue())

    def test_cli_writes_a_json_report_to_the_requested_path(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "records.jsonl"
            output = Path(directory) / "report.json"
            source.write_text('{"actor_id":"actor-1"}\n', encoding="utf-8")

            result = main([str(source), "--output", str(output)])

            report = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(report["dataset"]["record_count"], 1)


if __name__ == "__main__":
    unittest.main()
