"""Offline tests for the replay exporter, the viz server, and the static player files."""

import contextlib
import gzip
import http.client
import importlib.util
import io
import json
import re
import tempfile
import threading
import unittest
from copy import deepcopy
from pathlib import Path

from swarm_forensics import replay

ROOT = Path(__file__).resolve().parents[2]
VIZ = ROOT / "pug-research" / "experiments" / "viz_mock" / "v2"
SESSION = "11111111-2222-4333-8444-555555555555"
OTHER = "99999999-2222-4333-8444-555555555555"
AGENT = "agent-1"


def write_gz(path: Path, rows: list, raw_lines: list[str] | None = None) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
        for line in raw_lines or []:
            handle.write(line + "\n")


def turn(n: int, session: str = SESSION, **fields) -> dict:
    return {
        "id": f"turn-{n}",
        "session_id": session,
        "created_at": f"2026-02-03 04:05:{n:02d}.5",
        **fields,
    }


class ArchiveCase(unittest.TestCase):
    """Write a small fake archive set to a temporary directory."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def write_all(self, turns, events=(), session_extra=None):
        session = {
            "id": SESSION,
            "agent_id": AGENT,
            "created_at": "2026-02-03 04:05:00.0",
            "session_goal": "Goal text",
            **(session_extra or {}),
        }
        write_gz(self.dir / "computer_use_sessions.jsonl.gz", [session])
        write_gz(self.dir / "agents.jsonl.gz", [{"id": AGENT, "model_string": "claude-opus-9"}])
        write_gz(self.dir / "computer_use_turns.jsonl.gz", list(turns))
        write_gz(self.dir / "events.jsonl.gz", list(events))


class SanitizeTests(unittest.TestCase):
    def test_masks_credential_like_values(self):
        text = "curl -H 'Authorization: Bearer abcdefgh12345678' -d password=hunter2 hf_abcdefghij12"
        clean = replay.sanitize(text + " bob@example.org 10.1.2.3", 500)
        for secret in ("abcdefgh12345678", "hunter2", "hf_abcdefghij12", "bob@", "10.1.2.3"):
            self.assertNotIn(secret, clean.text)
        self.assertEqual(clean.masked, 5)

    def test_keeps_upstream_redaction_and_local_ip(self):
        clean = replay.sanitize("token=[REDACTED] host 127.0.0.1 git@github.com:x/y", 500)
        self.assertIn("token=[REDACTED]", clean.text)
        self.assertIn("127.0.0.1", clean.text)
        self.assertIn("git@github.com", clean.text)
        self.assertEqual((clean.masked, clean.markers), (0, 1))

    def test_truncates_with_a_note(self):
        clean = replay.sanitize("x" * 30, 10)
        self.assertEqual(clean.omitted, 20)
        self.assertTrue(clean.text.startswith("x" * 10))
        self.assertIn("20 characters omitted", clean.text)

    def test_non_text_becomes_empty(self):
        self.assertEqual(replay.sanitize(None, 10).text, "")
        self.assertEqual(replay.sanitize(42, 10).text, "")


class ParseTests(unittest.TestCase):
    def test_timestamp_forms(self):
        self.assertEqual(replay.iso(replay.parse_timestamp("2026-01-02 03:04:05")), "2026-01-02T03:04:05.000Z")
        self.assertEqual(replay.iso(replay.parse_timestamp("2026-01-02 03:04:05.5")), "2026-01-02T03:04:05.500Z")
        value = replay.parse_timestamp("2026-01-02 03:04:05.123456")
        self.assertEqual(value.microsecond, 123456)

    def test_bad_timestamp_hides_value(self):
        with self.assertRaises(replay.ReplayError) as caught:
            replay.parse_timestamp("not-a-secret-date")
        self.assertNotIn("secret", str(caught.exception))

    def test_hosts_skip_ips_and_userinfo(self):
        text = "curl https://user:pw@Api.Example.org:8443/x http://10.0.0.1/y https://a.b.co/z https://localhost/q"
        self.assertEqual(replay.hosts_in(text), ["api.example.org", "a.b.co"])

    def test_provider_heuristic(self):
        self.assertEqual(replay.provider_of("gpt-5"), "OpenAI")
        self.assertEqual(replay.provider_of("claude-code::claude-opus-4"), "Anthropic")
        self.assertEqual(replay.provider_of("zzz"), "Other")


class StepTests(unittest.TestCase):
    def step(self, **fields):
        return replay.step_from_turn(turn(1, **fields), SESSION, AGENT)

    def test_error_wins_over_output(self):
        step = self.step(agent_action={"command": "ls"}, output="a", error="boom")
        self.assertEqual(step["status"], "stderr_recorded")
        self.assertIn("does not prove failure", step["outcome_note"])

    def test_no_output_is_unknown(self):
        step = self.step(agent_action={"command": "ls"})
        self.assertEqual(step["status"], "no_output")
        self.assertIn("unknown", step["outcome_note"])

    def test_work_priority_and_signals(self):
        step = self.step(agent_action={"command": "python3 x.py && git push origin main"})
        self.assertEqual(step["work"], "git-push")
        self.assertIn("Python", step["signals"])

    def test_typed_text_is_not_exported(self):
        step = self.step(agent_action={"action": "type", "text": "my password"})
        self.assertNotIn("my password", json.dumps(step))
        self.assertEqual(step["surface"], "desktop")

    def test_malformed_action_falls_back(self):
        for action in (None, "text", [], {}):
            step = self.step(agent_action=action)
            self.assertEqual(step["surface"], "other")

    def test_truncation_is_flagged(self):
        step = self.step(agent_action={"command": "echo"}, output="y" * 5000)
        self.assertEqual(step["evidence"]["truncated"], ["output"])

    def test_requested_versus_referenced(self):
        fetch = self.step(agent_action={"command": "curl https://a.example.org/x"})
        mention = self.step(agent_action={"command": "echo https://b.example.org/x"})
        self.assertEqual(fetch["destinations"], [{"host": "a.example.org", "relation": "requested"}])
        self.assertEqual(mention["destinations"][0]["relation"], "referenced")


class ExportTests(ArchiveCase):
    def test_joins_orders_and_links(self):
        turns = [
            turn(9, agent_action={"command": "git push"}, error="denied"),
            turn(2, agent_action={"command": "curl https://x.example.org"}, output="ok"),
            turn(5, session=OTHER, agent_action={"command": "other"}),
        ]
        events = [
            {"id": "e1", "event_index": 3, "created_at": "2026-02-03 04:05:04", "data": {
                "actionType": "PAUSE", "agentId": AGENT, "seconds": 7}},
            {"id": "e2", "event_index": 4, "created_at": "2026-02-03 04:05:06", "data": {
                "actionType": "CONSOLIDATE", "computerUseSessionId": SESSION}},
            {"id": "e3", "event_index": 5, "created_at": "2026-02-03 09:00:00", "data": {
                "actionType": "PAUSE", "agentId": AGENT}},
            {"id": "e4", "event_index": 6, "created_at": "2026-02-03 04:05:05", "data": {
                "actionType": "PAUSE", "agentId": "someone-else"}},
        ]
        self.write_all(turns, events)
        case = replay.export_session(SESSION, self.dir)
        self.assertEqual([s["source"]["id"] for s in case["steps"]], ["turn-2", "turn-9"])
        self.assertEqual([s["i"] for s in case["steps"]], [1, 2])
        self.assertEqual(case["steps"][1]["t_ms"], 7000)
        self.assertEqual(case["actor"]["provider"], "Anthropic")
        links = {c["source"]["id"]: c["link"] for c in case["context"]}
        self.assertEqual(links, {"e1": "time_window", "e2": "session_id"})
        self.assertEqual(case["context"][0]["text"], "7 seconds")

    def test_missing_evidence_fields_are_tolerated(self):
        self.write_all([turn(1), turn(2, agent_action={"command": 5})])
        case = replay.export_session(SESSION, self.dir)
        self.assertEqual(len(case["steps"]), 2)
        self.assertEqual(case["steps"][0]["status"], "no_output")

    def test_limits_are_reported(self):
        rows = [turn(i % 60, agent_action={"command": "a"}) | {"id": f"t{i}"} for i in range(5)]
        self.write_all(rows)
        original = replay.MAX_STEPS
        replay.MAX_STEPS = 3
        self.addCleanup(setattr, replay, "MAX_STEPS", original)
        case = replay.export_session(SESSION, self.dir)
        self.assertEqual((len(case["steps"]), case["limits"]["turns_dropped"]), (3, 2))

    def test_secrets_never_reach_the_file(self):
        self.write_all([turn(1, agent_action={"command": "x token=abc12345"}, output="mail me@x.org")])
        case = replay.export_session(SESSION, self.dir)
        out = self.dir / "case.json"
        replay.write_case(case, out)
        text = out.read_text(encoding="utf-8")
        self.assertNotIn("abc12345", text)
        self.assertNotIn("me@x.org", text)
        self.assertEqual(case["limits"]["masked_values"], 2)

    def test_error_cases(self):
        with self.assertRaises(replay.ReplayError):
            replay.export_session("not-a-uuid", self.dir)
        with self.assertRaises(replay.ReplayError) as caught:
            replay.export_session(SESSION, self.dir)
        self.assertIn("file not found", str(caught.exception))
        self.write_all([])
        with self.assertRaises(replay.ReplayError) as caught:
            replay.export_session(SESSION, self.dir)
        self.assertIn("no recorded turns", str(caught.exception))
        with self.assertRaises(replay.ReplayError) as caught:
            replay.export_session(OTHER, self.dir)
        self.assertIn("not found", str(caught.exception))

    def test_malformed_json_message_hides_record(self):
        self.write_all([turn(1, agent_action={"command": "x"})])
        write_gz(
            self.dir / "computer_use_turns.jsonl.gz",
            [],
            raw_lines=[f'{{"session_id": "{SESSION}", "secret": "topsecret" BROKEN']
        )
        with self.assertRaises(replay.ReplayError) as caught:
            replay.export_session(SESSION, self.dir)
        message = str(caught.exception)
        self.assertIn("malformed JSON on line 1", message)
        self.assertNotIn("topsecret", message)

    def test_damaged_gzip(self):
        self.write_all([turn(1)])
        (self.dir / "events.jsonl.gz").write_bytes(b"not gzip data")
        with self.assertRaises(replay.ReplayError) as caught:
            replay.export_session(SESSION, self.dir)
        self.assertIn("damaged", str(caught.exception))

    def test_cli(self):
        self.write_all([turn(1, agent_action={"command": "ls"}, output="x")])
        out = self.dir / "nested" / "case.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = replay.main(["--session", SESSION, "--dir", str(self.dir), "--out", str(out)])
        self.assertEqual(code, 0)
        replay.validate_case(json.loads(out.read_text(encoding="utf-8")))
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code = replay.main(["--session", OTHER, "--dir", str(self.dir)])
        self.assertEqual(code, 1)
        self.assertIn("Error:", errors.getvalue())


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.case = replay.build_mock_case()

    def test_mock_is_deterministic_and_valid(self):
        self.assertEqual(self.case, replay.build_mock_case())
        self.assertTrue(self.case["synthetic"])
        replay.validate_case(self.case)

    def test_mock_covers_each_status_and_a_destination(self):
        statuses = {s["status"] for s in self.case["steps"]}
        self.assertEqual(statuses, set(replay.STATUSES))
        self.assertTrue(any(s["destinations"] for s in self.case["steps"]))

    def test_rejects_broken_cases(self):
        def mutate(change):
            case = deepcopy(self.case)
            change(case)
            return case

        broken = {
            "version": lambda c: c.update(schema_version=99),
            "empty steps": lambda c: c.update(steps=[]),
            "missing key": lambda c: c["steps"][0].pop("evidence"),
            "gap": lambda c: c["steps"][1].update(i=7),
            "status": lambda c: c["steps"][0].update(status="success"),
            "surface": lambda c: c["steps"][0].update(surface="nope"),
            "duplicate": lambda c: c["steps"][1]["source"].update(id=c["steps"][0]["source"]["id"]),
            "order": lambda c: c["steps"][2].update(t_ms=-1),
            "relation": lambda c: c["steps"][1]["destinations"][0].update(relation="attacked"),
            "link": lambda c: c["context"][0].update(link="causal"),
            "not object": lambda c: c.update(actor="x"),
        }
        for name, change in broken.items():
            with self.subTest(name), self.assertRaises(replay.ReplayError):
                replay.validate_case(mutate(change))
        with self.assertRaises(replay.ReplayError):
            replay.validate_case([])

    def test_mock_masks_seeded_secret(self):
        text = json.dumps(self.case)
        for secret in ("abcd1234efgh5678", "admin@example.org", "10.1.2.3"):
            self.assertNotIn(secret, text)


def load_server():
    spec = importlib.util.spec_from_file_location("viz_serve", VIZ / "serve.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ServeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_server()
        cls.module.Handler.log_message = lambda *args: None
        cls.tmp = tempfile.TemporaryDirectory()
        cls.case = Path(cls.tmp.name) / "case.json"
        cls.case.write_text('{"ok": true}', encoding="utf-8")
        cls.server = cls.module.make_server(0, cls.case)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def fetch(self, path: str, method: str = "GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request(method, path)
            response = conn.getresponse()
            return response.status, response.getheader("Content-Type", ""), response.read()
        finally:
            conn.close()

    def test_default_case_stays_in_repository_raw_data(self):
        self.assertEqual(
            self.module.DEFAULT_CASE, ROOT / "data" / "raw" / "replay" / "sample-case.json"
        )

    def test_binds_to_loopback(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_case_route(self):
        status, kind, body = self.fetch("/case.json")
        self.assertEqual((status, body), (200, b'{"ok": true}'))
        self.assertIn("application/json", kind)
        self.assertEqual(self.fetch("/case.json?x=1")[0], 200)
        self.assertEqual(self.fetch("/case.json", "HEAD")[0], 200)

    def test_missing_case_is_404(self):
        server = self.module.make_server(0, Path(self.tmp.name) / "absent.json")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("GET", "/case.json")
        self.assertEqual(conn.getresponse().status, 404)
        conn.close()

    def test_public_files_are_served(self):
        for path in ("/workflow-player.html", "/vendor/three.module.min.js", "/vendor/OrbitControls.js"):
            self.assertEqual(self.fetch(path)[0], 200, path)
        self.assertIn("javascript", self.fetch("/vendor/OrbitControls.js")[1])

    def test_everything_else_is_refused(self):
        for path in (
            "/", "/vendor/", "/serve.py", "/../../../README.md", "/%2e%2e/%2e%2e/README.md",
            "/..%2f..%2f..%2fdata/raw/events.jsonl.gz", "/data/raw/replay/case.json",
            "/vendor/../serve.py", "/.hidden.json", "/missing.html",
        ):
            with self.subTest(path):
                self.assertEqual(self.fetch(path)[0], 404)


class FrontendTests(unittest.TestCase):
    """Static checks on the browser files. No browser runs here."""

    @classmethod
    def setUpClass(cls):
        cls.player = (VIZ / "workflow-player.html").read_text(encoding="utf-8")
        cls.daily = (VIZ / "pipeline-real-v3.html").read_text(encoding="utf-8")

    def test_player_loads_only_local_resources(self):
        urls = re.findall(r"""(?:src|href|from)\s*=?\s*["'](https?:)?//""", self.player)
        self.assertEqual(urls, [])
        self.assertNotIn("http://", self.player.replace("http://www.w3.org", ""))
        self.assertNotIn("https://", self.player)
        self.assertIn("./vendor/three.module.min.js", self.player)

    def test_player_reads_one_data_route(self):
        self.assertEqual(re.findall(r"fetch\(([^)]*)\)", self.player), ["'./case.json'"])

    def test_player_renders_record_text_safely(self):
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
            self.assertNotIn(banned, self.player)

    def test_player_has_playback_controls(self):
        for control in ("btn-play", "btn-prev", "btn-next", "btn-reset", "speed", "scrub"):
            self.assertIn(f'id="{control}"', self.player)

    def test_player_does_not_move_the_camera_on_playback(self):
        self.assertNotIn("autoFocus", self.player)
        self.assertNotIn("camera.position.lerp", self.player)

    def test_daily_player_has_no_auto_zoom(self):
        self.assertNotIn("autoFocus", self.daily)


if __name__ == "__main__":
    unittest.main()
