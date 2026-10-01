"""Offline tests for the schema validator. Fixtures are synthetic. No test uses the network."""

import contextlib
import copy
import gzip
import io
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from swarm_forensics.ingest import download, sample, schema

ID = "00000000-0000-4000-8000-000000000001"
STAMP = "2025-12-29 18:49:21.291984"
SECRET = "SECRET-RECORD-VALUE"

VALID = {
    "agents": {
        "id": ID, "name": "Agent", "model_string": "model", "goal": None, "is_participating": True,
        "input_tokens_used": 1, "money": "0.00", "paused_until": None, "current_room_id": ID,
        "village_id": ID, "created_at": STAMP, "updated_at": STAMP,
    },
    "events": {
        "id": ID, "event_index": 1, "village_id": ID, "created_at": STAMP, "updated_at": STAMP,
        "data": {"actionType": "AGENT_TALK", "speakerId": ID, "roomId": ID, "messageId": ID,
                 "content": "hello", "cost": 0.5, "inputTokens": 10, "output": [{"any": "shape"}]},
    },
    "chat_messages": {
        "id": ID, "speaker_type": "agent", "agent_speaker_id": ID, "user_speaker_id": None,
        "content": "hello", "room_id": ID, "has_been_approved": None, "created_at": STAMP,
    },
    "chat_rooms": {
        "id": ID, "name": "room", "deleted_at": None, "blacklisted_agent_names": None,
        "whitelisted_agent_names": ["a"], "created_at": STAMP,
    },
    "computer_use_sessions": {
        "id": ID, "agent_id": ID, "session_goal": "goal", "short_displayed_session_goal": None,
        "has_been_asked_to_stop": False, "created_at": STAMP,
    },
    "computer_use_turns": {
        "id": ID, "session_id": ID, "agent_action": {"action": "left_click"},
        "agent_messages": {"content": []}, "output": None, "error": None, "system": None,
        "screenshot_is_redacted": False, "has_redaction_been_overruled": None, "created_at": STAMP,
    },
    "agent_memories": {"id": ID, "content": "memory", "agent_id": ID, "created_at": STAMP},
    "summaries": {
        "id": ID, "type": "daily", "summary_target": None, "summary_date": "2025-04-02",
        "content": "text", "generated_by": "model", "created_at": STAMP,
    },
    "claude_code_messages": {
        "id": ID, "agent_id": ID, "sdk_session_id": "sdk", "message_type": "assistant",
        "message_subtype": None, "message_uuid": None, "content": {"message": {}},
        "created_at": STAMP,
    },
    "claude_code_sessions": {"id": ID, "agent_id": ID, "sdk_session_id": "sdk", "created_at": STAMP},
    "villages": {
        "id": ID, "name": "village", "slug": "village", "turn_id": None, "is_chat_open": True,
        "schedule": {}, "created_at": STAMP,
    },
    "village_goals": {"id": ID, "goal": "goal", "start_time": STAMP, "end_time": None},
    "agent_goals": {
        "id": ID, "agent_id": ID, "name": "n", "short_name": "s", "description": None,
        "start_time": None, "end_time": None,
    },
}


def write_gzip(path, lines):
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for line in lines:
            handle.write(line + "\n")


def rows(table, count):
    return [json.dumps(VALID[table]) for _ in range(count)]


class ContractTests(unittest.TestCase):
    def test_schema_document_is_valid(self):
        Draft202012Validator.check_schema(schema.load_schema())

    def test_every_downloaded_table_has_a_contract(self):
        self.assertEqual(set(schema.table_names()), set(download.TABLES))
        self.assertEqual(set(VALID), set(download.TABLES))
        for table in schema.table_names():
            self.assertIn(table, schema.load_schema()["$defs"])

    def test_valid_fixture_passes_for_every_table(self):
        for table, record in VALID.items():
            with self.subTest(table=table):
                schema.validate_record(table, record)

    def test_each_required_field_is_enforced(self):
        for table in schema.table_names():
            for field in schema.load_schema()["$defs"][table]["required"]:
                with self.subTest(table=table, field=field):
                    record = copy.deepcopy(VALID[table])
                    del record[field]
                    with self.assertRaises(schema.DatasetError) as context:
                        schema.validate_record(table, record, 7)
                    self.assertEqual(context.exception.path, f"$.{field}")
                    self.assertEqual(context.exception.line, 7)
                    self.assertIn("'required'", str(context.exception))

    def test_unknown_fields_are_allowed(self):
        for table, record in VALID.items():
            with self.subTest(table=table):
                schema.validate_record(table, {**record, "future_field": {"a": 1}})

    def test_unknown_table_is_rejected(self):
        with self.assertRaisesRegex(schema.DatasetError, "unknown table"):
            schema.validate_record("images", {})

    def test_record_must_be_an_object(self):
        with self.assertRaises(schema.DatasetError) as context:
            schema.validate_record("events", ["not", "an", "object"])
        self.assertEqual(context.exception.path, "$")


class FieldRuleTests(unittest.TestCase):
    def check_fails(self, table, change, path, rule):
        record = copy.deepcopy(VALID[table])
        change(record)
        with self.assertRaises(schema.DatasetError) as context:
            schema.validate_record(table, record)
        self.assertEqual(context.exception.path, path)
        self.assertIn(f"'{rule}'", str(context.exception))

    def test_null_is_rejected_for_identifiers(self):
        self.check_fails("events", lambda r: r.update(id=None), "$.id", "type")

    def test_nullable_fields_accept_null(self):
        record = copy.deepcopy(VALID["agent_goals"])
        record.update(description=None, start_time=None, end_time=None)
        schema.validate_record("agent_goals", record)
        record = copy.deepcopy(VALID["chat_messages"])
        record.update(agent_speaker_id=None, has_been_approved=None)
        schema.validate_record("chat_messages", record)

    def test_uuid_shape(self):
        self.check_fails(
            "chat_messages", lambda r: r.update(room_id="not-a-uuid"), "$.room_id", "pattern"
        )

    def test_timestamp_shapes(self):
        for good in (STAMP, "2025-12-29T18:49:21Z", "2025-12-29 18:49:21+00:00"):
            record = copy.deepcopy(VALID["agent_memories"])
            record["created_at"] = good
            schema.validate_record("agent_memories", record)
        self.check_fails(
            "agent_memories", lambda r: r.update(created_at="yesterday"), "$.created_at", "pattern"
        )

    def test_wrong_scalar_type(self):
        self.check_fails("events", lambda r: r.update(event_index="1"), "$.event_index", "type")
        self.check_fails(
            "computer_use_sessions",
            lambda r: r.update(has_been_asked_to_stop="no"),
            "$.has_been_asked_to_stop",
            "type",
        )

    def test_event_variants(self):
        unknown = copy.deepcopy(VALID["events"])
        unknown["data"] = {"actionType": "FUTURE_ACTION", "extra": 1}
        schema.validate_record("events", unknown)
        self.check_fails("events", lambda r: r["data"].pop("actionType"), "$.data.actionType", "required")
        self.check_fails(
            "events", lambda r: r["data"].update(messageId="x"), "$.data.messageId", "pattern"
        )
        self.check_fails("events", lambda r: r.update(data="text"), "$.data", "type")

    def test_event_output_keeps_any_provider_shape(self):
        for output in ({"candidates": []}, [{"type": "reasoning"}], "text", None, 3):
            record = copy.deepcopy(VALID["events"])
            record["data"]["output"] = output
            schema.validate_record("events", record)

    def test_agent_messages_accept_object_or_array(self):
        for payload in ({"content": []}, [{"type": "function_call"}]):
            record = copy.deepcopy(VALID["computer_use_turns"])
            record["agent_messages"] = payload
            schema.validate_record("computer_use_turns", record)
        self.check_fails(
            "computer_use_turns",
            lambda r: r.update(agent_messages="text"),
            "$.agent_messages",
            "type",
        )

    def test_claude_code_content_must_be_an_object(self):
        self.check_fails(
            "claude_code_messages", lambda r: r.update(content="text"), "$.content", "type"
        )

    def test_relationships_are_annotated(self):
        defs = schema.load_schema()["$defs"]
        self.assertEqual(defs["computer_use_turns"]["properties"]["session_id"]["x-references"],
                         "computer_use_sessions.id")
        self.assertEqual(defs["computer_use_sessions"]["properties"]["agent_id"]["x-references"],
                         "agents.id")

    def test_source_revision_is_recorded(self):
        self.assertRegex(schema.load_schema()["x-source"]["revision"], r"^[0-9a-f]{40}$")


class SafeDiagnosticsTests(unittest.TestCase):
    def test_record_values_are_not_reported(self):
        record = copy.deepcopy(VALID["chat_messages"])
        record["room_id"] = SECRET
        with self.assertRaises(schema.DatasetError) as context:
            schema.validate_record("chat_messages", record, 3)
        self.assertNotIn(SECRET, str(context.exception))
        self.assertEqual(str(context.exception), "chat_messages: line 3: $.room_id: rule 'pattern' failed")

    def test_malformed_json_is_reported_without_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl.gz"
            write_gzip(path, rows("events", 1) + [f"{{{SECRET}"])
            with self.assertRaises(schema.DatasetError) as context:
                list(schema.iter_records(path, "events"))
        self.assertEqual(context.exception.line, 2)
        self.assertIn("malformed JSON", str(context.exception))
        self.assertNotIn(SECRET, str(context.exception))


class StreamingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "events.jsonl.gz"

    def test_records_are_read_lazily(self):
        write_gzip(self.path, rows("events", 1) + ["not json"])
        records = schema.iter_records(self.path, "events")
        self.assertEqual(next(records)["event_index"], 1)
        with self.assertRaisesRegex(schema.DatasetError, "malformed JSON"):
            next(records)

    def test_limit_stops_before_later_rows(self):
        write_gzip(self.path, rows("events", 2) + ["not json"])
        self.assertEqual(len(list(schema.iter_records(self.path, "events", limit=2))), 2)

    def test_blank_lines_are_skipped_and_line_numbers_kept(self):
        bad = json.dumps({"id": ID})
        write_gzip(self.path, rows("events", 1) + ["", bad])
        with self.assertRaises(schema.DatasetError) as context:
            list(schema.iter_records(self.path, "events"))
        self.assertEqual(context.exception.line, 3)

    def test_check_table_reports_limit_and_end_of_file(self):
        write_gzip(self.path, rows("events", 5))
        self.assertEqual(schema.check_table(self.path, "events", 3), schema.TableReport("events", 3, False))
        self.assertEqual(schema.check_table(self.path, "events", 5), schema.TableReport("events", 5, True))
        self.assertEqual(schema.check_table(self.path, "events", None), schema.TableReport("events", 5, True))

    def test_missing_file(self):
        with self.assertRaisesRegex(schema.DatasetError, "file not found"):
            list(schema.iter_records(self.path, "events"))

    def test_damaged_archive(self):
        write_gzip(self.path, rows("events", 200))
        self.path.write_bytes(self.path.read_bytes()[:-20])
        with self.assertRaisesRegex(schema.DatasetError, "damaged or unreadable"):
            list(schema.iter_records(self.path, "events"))

    def test_file_that_is_not_gzip(self):
        self.path.write_bytes(b"plain text, not gzip\n")
        with self.assertRaisesRegex(schema.DatasetError, "damaged or unreadable"):
            list(schema.iter_records(self.path, "events"))


class SampleTests(unittest.TestCase):
    def test_sample_tables_satisfy_the_contracts(self):
        for table, records in sample.build_tables(50).items():
            for number, record in enumerate(records, start=1):
                schema.validate_record(table, record, number)

    def test_sample_covers_agent_and_user_events(self):
        events = sample.build_tables(10)["events"]
        types = {event["data"]["actionType"] for event in events}
        self.assertLessEqual({"AGENT_TALK", "USER_TALK"}, types)


class CommandTests(unittest.TestCase):
    def run_command(self, argv):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = schema.main(argv)
        return code, output.getvalue(), errors.getvalue()

    def test_validates_sample_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            sample.write_sample(Path(directory), rows=10)
            code, output, _ = self.run_command(["--dir", directory])
        self.assertEqual(code, 0)
        self.assertIn("events: 10 records checked, reached end of file", output)
        self.assertIn("Validated 3 tables", output)
        self.assertNotIn("limited", output)

    def test_limited_run_is_labelled(self):
        with tempfile.TemporaryDirectory() as directory:
            sample.write_sample(Path(directory), rows=10)
            code, output, _ = self.run_command(["--dir", directory, "--limit", "4"])
        self.assertEqual(code, 0)
        self.assertIn("events: 4 records checked, stopped at limit 4", output)
        self.assertIn("does not cover the whole dataset", output)

    def test_zero_limit_scans_every_record(self):
        with tempfile.TemporaryDirectory() as directory:
            sample.write_sample(Path(directory), rows=150)
            code, output, _ = self.run_command(["--dir", directory, "--limit", "0"])
        self.assertEqual(code, 0)
        self.assertIn("events: 150 records checked, reached end of file", output)

    def test_default_scan_stops_at_100_records(self):
        with tempfile.TemporaryDirectory() as directory:
            sample.write_sample(Path(directory), rows=150)
            _, output, _ = self.run_command(["--dir", directory])
        self.assertIn("events: 100 records checked, stopped at limit 100", output)

    def test_fails_when_no_supported_table_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            code, _, errors = self.run_command(["--dir", directory])
        self.assertEqual(code, 1)
        self.assertIn("no supported table files found", errors)

    def test_fails_when_a_requested_table_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            sample.write_sample(Path(directory), rows=5)
            code, output, errors = self.run_command(["--dir", directory, "--tables", "events", "agents"])
        self.assertEqual(code, 1)
        self.assertIn("agents: file not found", errors)
        self.assertEqual(output, "")

    def test_selected_tables_only(self):
        with tempfile.TemporaryDirectory() as directory:
            sample.write_sample(Path(directory), rows=5)
            code, output, _ = self.run_command(["--dir", directory, "--tables", "agent_goals"])
        self.assertEqual(code, 0)
        self.assertIn("Validated 1 tables", output)
        self.assertNotIn("events:", output)

    def test_invalid_record_fails_the_command(self):
        with tempfile.TemporaryDirectory() as directory:
            write_gzip(Path(directory) / "events.jsonl.gz", [json.dumps({"id": ID})])
            code, _, errors = self.run_command(["--dir", directory])
        self.assertEqual(code, 1)
        self.assertIn("events: line 1: $.event_index: rule 'required' failed", errors)

    def test_unknown_table_and_negative_limit_are_usage_errors(self):
        for argv in (["--tables", "images"], ["--limit", "-1"]):
            with self.subTest(argv=argv), self.assertRaises(SystemExit) as context:
                self.run_command(argv)
            self.assertEqual(context.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
