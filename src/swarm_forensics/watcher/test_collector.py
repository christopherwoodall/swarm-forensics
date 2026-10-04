"""Test the collector with synthetic source pages."""

import contextlib
import importlib
import importlib.util
import io
import json
import subprocess
import tempfile
import time
import unittest
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path

SESSION = "ca8ffac066a4"


def event(seq=1, **updates):
    value = {"seq": seq, "at": 1700000000, "author": {"name": "Synthetic human"},
             "kind": "message", "text": "Synthetic proposal"}
    value.update(updates)
    return value


def page(events=None, cursor=1, **updates):
    value = {"session_id": SESSION, "access_mode": "conversation",
             "events": [event()] if events is None else events,
             "has_more": False, "next_cursor": cursor,
             "participant": {"expires_at": 2000000000}, "tasks": []}
    value.update(updates)
    return json.dumps(value).encode()


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "source.sqlite"

    def collector(self):
        self.assertIsNotNone(importlib.util.find_spec("swarm_forensics.watcher.collector"),
                             "The source collector is missing")
        return importlib.import_module("swarm_forensics.watcher.collector")

    def test_capture_survives_restart_without_acknowledgement(self):
        module = self.collector()
        raw = page()
        with module.Archive(self.path) as archive:
            self.assertEqual(archive.capture(raw, after=0, captured_at=1700000010), 1)
        with module.Archive(self.path) as archive:
            self.assertEqual(archive.status()["read_cursor"], 1)
            self.assertEqual(archive.status()["processed_cursor"], 0)
            self.assertEqual(archive.pending()["events"], [event()])
            self.assertEqual(archive.connection.execute("SELECT payload FROM pages").fetchone()[0],
                             raw)

    def test_replay_deduplicates_and_changed_identity_rolls_back(self):
        module = self.collector()
        with module.Archive(self.path) as archive:
            archive.capture(page(), after=0, captured_at=10)
            self.assertEqual(archive.capture(page(), after=1, captured_at=11), 0)
            with self.assertRaisesRegex(module.SourceError, "changed source"):
                archive.capture(page([event(2), event(text="Changed")], cursor=2),
                                after=1, captured_at=12)
            self.assertEqual(archive.pending()["events"], [event()])
            self.assertEqual(archive.status()["read_cursor"], 1)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
                             2)

    def test_pending_is_bounded_and_ack_is_a_separate_durable_action(self):
        module = self.collector()
        with module.Archive(self.path) as archive:
            archive.capture(page([event(1), event(5), event(8)], cursor=9),
                            after=0, captured_at=10)
            first = archive.pending(limit=2)
            self.assertEqual(first["events"], [event(1), event(5)])
            self.assertEqual(first["next_cursor"], 5)
            self.assertTrue(first["has_more"])
            self.assertEqual(archive.status()["pending_count"], 3)
            archive.ack(first["next_cursor"])
        with module.Archive(self.path) as archive:
            self.assertEqual(archive.pending()["events"], [event(8)])
            for cursor in (4, 10, -1, True, 1.5):
                with self.subTest(cursor=cursor), self.assertRaises(module.SourceError):
                    archive.ack(cursor)
            self.assertEqual(archive.status()["processed_cursor"], 5)
            archive.ack(9)
            archive.ack(9)
            self.assertEqual(archive.pending()["events"], [])
            for limit in (0, -1, True, 1001):
                with self.subTest(limit=limit), self.assertRaises(module.SourceError):
                    archive.pending(limit)

    def test_invalid_bound_pages_leave_the_archive_empty(self):
        module = self.collector()
        invalid = [page(session_id="other"), page(access_mode="relationship"),
                   page(has_more=True, cursor=0, events=[]), page(cursor=-1),
                   page(cursor=True), page(has_more=1), page(cursor=0),
                   page(events=[event(0)]), page(events=[event(True)]),
                   page(events=[event(at=float("nan"))]), page(events=[event(author="human")]),
                   page(events=[event(text=None)]), page(events=[event(kind=3)]),
                   page(events=[event(1), event(1)]), page(events={}),
                   page(participant={}), b"[]", b"not JSON",
                   b'{"session_id":"other","session_id":"ca8ffac066a4"}',
                   b" " * (2 * 1024 * 1024 + 1)]
        with module.Archive(self.path) as archive:
            for raw in invalid:
                with self.subTest(raw=raw[:80]), self.assertRaises(module.SourceError):
                    archive.capture(raw, after=0, captured_at=10)
                self.assertEqual(archive.status()["read_cursor"], 0)
                self.assertEqual(archive.status()["pending_count"], 0)
                self.assertEqual(archive.connection.execute(
                    "SELECT COUNT(*) FROM pages").fetchone()[0], 0)

    def test_get_reader_uses_only_the_fixed_route_and_bounded_timeout(self):
        module = self.collector()
        calls = []

        class Response:
            status = 200

            def __enter__(self):
                self.remaining = page()
                return self

            def __exit__(self, *args):
                pass

            def geturl(self):
                return module.ORIGIN + "/api/external-agents/session?after=7"

            def read1(self, limit):
                result, self.remaining = self.remaining[:limit], self.remaining[limit:]
                return result

        class Opener:
            def open(self, request, timeout):
                calls.append((request, timeout))
                return Response()

        self.assertTrue(hasattr(module, "PeerReader"), "The GET reader is missing")
        reader = module.PeerReader({"origin": module.ORIGIN, "token": "synthetic-token"},
                                   opener=Opener(), monotonic=lambda: 20)
        self.assertEqual(reader.fetch(7, deadline=25), page())
        request, timeout = calls[0]
        self.assertEqual(request.full_url,
                         "https://multi.fairystack.com/api/external-agents/session?after=7")
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        self.assertEqual(request.get_header("X-fairystack-agent-token"), "synthetic-token")
        self.assertEqual(timeout, 5)
        for after in (-1, True, 1.5):
            with self.subTest(after=after), self.assertRaises(module.SourceError):
                reader.fetch(after, deadline=25)
        with self.assertRaises(module.SourceError):
            reader.fetch(7, deadline=20)
        self.assertEqual(len(calls), 1)

    def test_reader_rejects_origins_and_all_redirects_without_leaking_tokens(self):
        module = self.collector()
        for origin in ("https://evil.invalid", module.ORIGIN + "/", module.ORIGIN + ":443",
                       "http://multi.fairystack.com", module.ORIGIN + "@evil.invalid"):
            with self.subTest(origin=origin), self.assertRaises(module.SourceError):
                module.PeerReader({"origin": origin, "token": "synthetic-token"})
        for token in ("", "bad\r\nheader", None):
            with self.subTest(token=token), self.assertRaises(module.SourceError):
                module.PeerReader({"origin": module.ORIGIN, "token": token})
        self.assertTrue(hasattr(module, "NoRedirect"), "Redirect protection is missing")
        for code in (301, 302, 303, 307, 308):
            for target in ("https://evil.invalid/steal", module.ORIGIN + "/api/post"):
                calls = []

                class FakeHTTPS(urllib.request.HTTPSHandler):
                    def https_open(self, request, calls=calls, target=target, code=code):
                        calls.append(request)
                        headers = Message()
                        headers["Location"] = target
                        response = urllib.response.addinfourl(io.BytesIO(b"private error"),
                                                              headers, request.full_url, code)
                        response.msg = "Redirect"
                        return response

                opener = urllib.request.build_opener(module.NoRedirect(), FakeHTTPS())
                reader = module.PeerReader({"origin": module.ORIGIN, "token": "secret"},
                                           opener=opener, monotonic=lambda: 0)
                with self.subTest(code=code, target=target), self.assertRaises(module.SourceError):
                    reader.fetch(0, deadline=5)
                self.assertEqual(len(calls), 1)
                self.assertEqual(calls[0].get_method(), "GET")

    def test_poll_archives_pages_and_refuses_network_after_stored_lease_expiry(self):
        module = self.collector()
        self.assertTrue(hasattr(module, "poll"), "The bounded poll is missing")
        calls = []
        replies = [page(cursor=1, has_more=True, participant={"expires_at": 100}),
                   page([event(4, author={"kind": "agent"})], cursor=6,
                        participant={"expires_at": 100})]

        def fetch(after, *, deadline):
            calls.append((after, deadline))
            return replies.pop(0)

        with module.Archive(self.path) as archive:
            result = module.poll(archive, fetch, now=lambda: 90, monotonic=lambda: 10,
                                 total_seconds=20, max_pages=3)
            self.assertEqual(calls, [(0, 30), (1, 30)])
            self.assertEqual(result["added_events"], 2)
            self.assertEqual(result["pages"], 2)
            self.assertTrue(result["caught_up"])
        with module.Archive(self.path) as archive:
            self.assertEqual(archive.status()["lease_expires_at"], 100)
            self.assertEqual(archive.pending()["events"][1]["author"], {"kind": "agent"})
            with self.assertRaisesRegex(module.SourceError, "lease expired"):
                module.poll(archive, fetch, now=lambda: 100)
            self.assertEqual(len(calls), 2)
            self.assertEqual(archive.status()["read_cursor"], 6)

    def test_poll_rejects_late_responses_and_invalid_resource_bounds(self):
        module = self.collector()
        clock = [0]
        calls = []

        def late(after, *, deadline):
            calls.append(after)
            clock[0] = deadline + 1
            return page()

        with module.Archive(self.path) as archive:
            with self.assertRaisesRegex(module.SourceError, "deadline"):
                module.poll(archive, late, total_seconds=5, monotonic=lambda: clock[0])
            self.assertEqual(archive.status()["read_cursor"], 0)
            for bounds in ({"max_pages": 0}, {"max_pages": True}, {"max_pages": 1001},
                           {"total_seconds": 0}, {"total_seconds": float("inf")},
                           {"total_seconds": 301}):
                with self.subTest(bounds=bounds), self.assertRaises(module.SourceError):
                    module.poll(archive, late, **bounds)
            self.assertEqual(calls, [0])

    def test_stale_or_failed_archive_transactions_do_not_advance(self):
        module = self.collector()
        with module.Archive(self.path) as archive:
            archive.capture(page(), after=0, captured_at=10)
            with self.assertRaisesRegex(module.SourceError, "stale"):
                archive.capture(page([event(2)], cursor=2), after=0, captured_at=11)
            archive.connection.execute("""
                CREATE TRIGGER fail_archive BEFORE INSERT ON pages
                BEGIN SELECT RAISE(ABORT, 'synthetic disk failure'); END
            """)
            with self.assertRaises(module.sqlite3.DatabaseError):
                archive.capture(page([event(2)], cursor=2), after=1, captured_at=11)
            self.assertEqual(archive.pending()["events"], [event()])
            self.assertEqual(archive.status()["read_cursor"], 1)

    def test_change_detector_stays_idle_and_retries_only_backlog_on_later_ticks(self):
        module = self.collector()
        with module.Archive(self.path) as archive:
            self.assertTrue(hasattr(archive, "change_token"), "The change detector is missing")
            self.assertEqual(archive.change_token(now=10, retry_seconds=60), "WATCHER_IDLE")
            archive.capture(page(), after=0, captured_at=10)
            first = archive.change_token(now=10, retry_seconds=60)
            self.assertIn("generation=1", first)
            self.assertTrue(first.startswith("WATCHER_WAKE "))
        with module.Archive(self.path) as archive:
            self.assertEqual(archive.change_token(now=11, retry_seconds=60), "WATCHER_IDLE")
            archive.capture(page([], cursor=2, tasks=[{"status": "volatile"}],
                                 participant={"expires_at": 2000000001}),
                            after=1, captured_at=12)
            self.assertEqual(archive.change_token(now=69, retry_seconds=60), "WATCHER_IDLE")
            retry = archive.change_token(now=70, retry_seconds=60)
            self.assertIn("generation=2", retry)
            archive.capture(page([event(3)], cursor=3), after=2, captured_at=71)
            self.assertIn("generation=3", archive.change_token(now=71, retry_seconds=60))
            archive.ack(3)
            for tick in (72, 100, 1000):
                self.assertEqual(archive.change_token(now=tick, retry_seconds=60), "WATCHER_IDLE")
            with self.assertRaises(module.SourceError):
                archive.change_token(now=1001, retry_seconds=0)

    def test_cli_poll_pending_ack_and_status_have_machine_readable_stdout(self):
        self.assertIsNotNone(importlib.util.find_spec("swarm_forensics.watcher.__main__"),
                             "The collector CLI is missing")
        cli = importlib.import_module("swarm_forensics.watcher.__main__")

        def run(*arguments, **options):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main(["--db", str(self.path), *arguments], **options)
            self.assertEqual(code, 0)
            return json.loads(out.getvalue())

        def fetch(after, *, deadline):
            return page([event(1), event(2)], cursor=2)

        self.assertEqual(run("poll", fetch=fetch)["added_events"], 2)
        pending = run("pending", "--limit", "1")
        self.assertEqual(pending["next_cursor"], 1)
        self.assertEqual(run("status")["processed_cursor"], 0)
        self.assertEqual(run("ack", "--cursor", "1")["processed_cursor"], 1)
        self.assertEqual(run("pending")["events"], [event(2)])

    def test_monitor_retries_failed_extraction_without_ack_or_idle_wakes(self):
        cli = importlib.import_module("swarm_forensics.watcher.__main__")
        module = self.collector()
        with module.Archive(self.path) as archive:
            archive.capture(page(), after=0, captured_at=10)

        def failed(after, *, deadline):
            raise module.SourceError("synthetic disconnected peer")

        def tick(timestamp):
            out, errors = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errors):
                code = cli.main(["--db", str(self.path), "monitor", "--retry-seconds", "60"],
                                fetch=failed, now=lambda: timestamp)
            self.assertEqual(code, 1)
            self.assertIn("disconnected", errors.getvalue())
            return out.getvalue().strip()

        self.assertTrue(tick(10).startswith("WATCHER_WAKE "))
        self.assertEqual(tick(11), "WATCHER_IDLE")
        self.assertEqual(tick(69), "WATCHER_IDLE")
        self.assertIn("generation=2", tick(70))
        with module.Archive(self.path) as archive:
            self.assertEqual(archive.status()["processed_cursor"], 0)
            archive.ack(1)
        self.assertEqual(tick(1000), "WATCHER_IDLE")

    def test_make_read_emits_only_json_and_lint_owns_both_viewer_checks(self):
        root = Path(__file__).resolve().parents[3]
        fake_client = Path(self.temp.name) / "synthetic_client.py"
        fake_client.write_text('import json\nprint(json.dumps({"synthetic": True}))\n')
        result = subprocess.run(
            ["make", "--no-print-directory", "watcher-read", "RUN=uv run --frozen",
             f"WATCHER_CLIENT={fake_client}", "WATCHER_CONFIG=synthetic-unused.json"],
            cwd=root, capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"synthetic": True})
        makefile = (root / "Makefile").read_text()
        lint_recipe = makefile.split("lint: setup", 1)[1].split("watcher-client:", 1)[0]
        self.assertIn("data/viz_mock/v2/serve.py data/viz_mock/v3_transluce/serve.py", lint_recipe)

    def test_make_collector_targets_are_frozen_without_setup_or_network_for_local_reads(self):
        root = Path(__file__).resolve().parents[3]
        base = ["make", "--no-print-directory", f"WATCHER_DB={self.path}",
                "WATCHER_CONFIG=synthetic-missing.json"]
        for command in ("watcher-status", "watcher-pending", "watcher-ack"):
            result = subprocess.run([*base, command, "WATCHER_CURSOR=0"], cwd=root,
                                    capture_output=True, text=True, timeout=30, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["read_cursor"], 0)
        preview = subprocess.run([*base, "--dry-run", "watcher-poll", "watcher-monitor"],
                                 cwd=root, capture_output=True, text=True, check=False)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertNotIn("uv sync", preview.stdout)
        self.assertEqual(preview.stdout.count("uv run --frozen"), 2)
        self.assertIn("--max-pages", preview.stdout)
        self.assertIn("--total-seconds", preview.stdout)
        self.assertIn("--retry-seconds", preview.stdout)

    def test_poll_wall_deadline_interrupts_a_blocked_fetch_offline(self):
        module = self.collector()

        def blocked(after, *, deadline):
            time.sleep(0.5)
            return page()

        with module.Archive(self.path) as archive:
            start = time.monotonic()
            with self.assertRaisesRegex(module.SourceError, "deadline"):
                module.poll(archive, blocked, total_seconds=0.05)
            self.assertLess(time.monotonic() - start, 0.4)
            self.assertEqual(archive.status()["read_cursor"], 0)

    def test_unseen_events_below_read_cursor_cannot_bypass_acknowledgement(self):
        module = self.collector()
        with module.Archive(self.path) as archive:
            archive.capture(page(cursor=5), after=0, captured_at=10)
            archive.ack(5)
            with self.assertRaisesRegex(module.SourceError, "unseen replay"):
                archive.capture(page([event(3)], cursor=5), after=5, captured_at=11)
            self.assertEqual(archive.status()["pending_count"], 0)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                             1)

    def test_poll_page_cap_is_resumable_and_later_failure_keeps_earlier_pages(self):
        module = self.collector()
        calls = []

        def fetch(after, *, deadline):
            calls.append(after)
            if after >= 2:
                raise module.SourceError("synthetic HTTP failure")
            return page([event(after + 1)], cursor=after + 1, has_more=True)

        with module.Archive(self.path) as archive:
            result = module.poll(archive, fetch, max_pages=1)
            self.assertEqual(result["stop_reason"], "page_cap")
            self.assertFalse(result["caught_up"])
            self.assertEqual(result["pages"], 1)
        with module.Archive(self.path) as archive:
            with self.assertRaises(module.SourceError):
                module.poll(archive, fetch)
            self.assertEqual(calls, [0, 1, 2])
            self.assertEqual(archive.status()["read_cursor"], 2)
            self.assertEqual(archive.status()["processed_cursor"], 0)
            self.assertEqual(archive.pending()["events"], [event(1), event(2)])
            with self.assertRaises(module.SourceError):
                module.poll(archive, lambda after, **kwargs: page([], cursor=2, has_more=True))
            self.assertEqual(archive.status()["read_cursor"], 2)


if __name__ == "__main__":
    unittest.main()
