"""Offline tests for the read-only Discord source archive."""

import contextlib
import io
import json
import os
import stat
import tempfile
import time
import unittest
import urllib.error
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path
from unittest.mock import patch

from swarm_forensics.watcher import discord_source as source

CHANNEL = "1430962817045106792"
GUILD = "1430962816315031654"


def message(identifier, **changes):
    item = {"id": str(identifier), "channel_id": CHANNEL,
            "author": {"id": "123456789012345678", "username": "Fictional"},
            "timestamp": "2026-01-01T00:00:00.000000+00:00", "content": "Synthetic text"}
    item.update(changes)
    return item


def page(*items):
    return json.dumps(list(items)).encode("utf-8")


class DiscordSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "source.sqlite"

    def test_capture_keeps_raw_page_and_does_not_ack(self):
        raw = page(message(120), message(110))
        with source.Archive(self.db) as archive:
            self.assertEqual(archive.capture(raw, before=None, captured_at=42), 2)
        with source.Archive(self.db) as archive:
            self.assertEqual(archive.status()["read_cursor"], 0)
            self.assertEqual(archive.status()["processed_cursor"], 0)
            self.assertEqual(archive.status()["pending_count"], 0)
            self.assertEqual(archive.connection.execute("SELECT payload FROM pages").fetchone()[0], raw)
            self.assertEqual(archive.status()["scan_before"], 110)

    def test_pagination_resumes_after_page_cap_before_releasing_pending(self):
        items = [message(identifier) for identifier in range(301, 196, -1)]
        calls = []

        def fetch(before, *, deadline):
            calls.append(before)
            available = [item for item in items if before is None or int(item["id"]) < before]
            return page(*available[:100])

        with source.Archive(self.db) as archive:
            receipt = source.poll(archive, fetch, max_pages=1)
            self.assertEqual(receipt["stop_reason"], "page_cap")
            self.assertTrue(receipt["gap"])
            self.assertEqual(receipt["read_cursor"], 0)
            self.assertEqual(archive.pending()["events"], [])
        with source.Archive(self.db) as archive:
            receipt = source.poll(archive, fetch)
            self.assertTrue(receipt["caught_up"])
            self.assertEqual(receipt["read_cursor"], 301)
            self.assertEqual(receipt["coverage_start"], 197)
            self.assertFalse(receipt["gap"])
            self.assertEqual(receipt["pending_count"], 105)
            first = archive.pending(limit=2)
            self.assertEqual([item["id"] for item in first["events"]], ["197", "198"])
            self.assertEqual(first["next_cursor"], 198)
            self.assertTrue(first["has_more"])
            archive.ack(198)
            self.assertEqual(archive.pending(limit=1)["events"][0]["id"], "199")
        self.assertEqual(calls, [None, 202, 197])

    def test_incremental_burst_walks_back_to_old_high_water(self):
        items = [message(identifier) for identifier in range(255, 99, -1)]
        calls = []

        def fetch(before, *, deadline):
            calls.append(before)
            return page(*[item for item in items
                           if before is None or int(item["id"]) < before][:100])

        with source.Archive(self.db) as archive:
            source.poll(archive, lambda before, **_: page(message(100))
                        if before is None else page())
            archive.ack(100)
            result = source.poll(archive, fetch, max_pages=1)
            self.assertEqual(result["read_cursor"], 100)
            self.assertTrue(result["gap"])
            self.assertEqual(result["pending_count"], 0)
        with source.Archive(self.db) as archive:
            result = source.poll(archive, fetch)
            self.assertEqual(result["read_cursor"], 255)
            self.assertEqual(result["pending_count"], 155)
            self.assertEqual(archive.pending(limit=1)["events"][0]["id"], "101")
            result = source.poll(archive, fetch)
            self.assertEqual(result["added_events"], 0)
            self.assertEqual(result["pending_count"], 155)
        self.assertEqual(calls, [None, 156, None])

    def test_invalid_source_pages_leave_raw_and_events_unchanged(self):
        invalid = [page(message(2, timestamp="not a timestamp")),
                   page(message(2, channel_id="999")),
                   page(message(2, author={"username": "Anonymous"})),
                   page(message(2, id="02")),
                   page(message(2, id="9223372036854775808")),
                   page(message(2), message(3)),
                   page(message(2), message(2)),
                   page(*[message(i) for i in range(101, 0, -1)]),
                   b'{"id":"2","id":"3"}', b"not JSON", b"{}",
                   b" " * (source.MAX_PAGE_BYTES + 1)]
        with source.Archive(self.db) as archive:
            for raw in invalid:
                with self.subTest(raw=raw[:50]), self.assertRaises(source.SourceError):
                    archive.capture(raw, before=None, captured_at=10)
                self.assertEqual(archive.status()["read_cursor"], 0)
                self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 0)
                self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], 0)

    def test_changed_payload_rolls_back_whole_page_and_keeps_cursor(self):
        with source.Archive(self.db) as archive:
            source.poll(archive, lambda before, **_: page(message(100))
                        if before is None else page())
            raw = page(message(105), message(100, content="Edited"))
            with self.assertRaisesRegex(source.SourceError, "changed source"):
                archive.capture(raw, before=None, captured_at=11)
            self.assertEqual(archive.status()["read_cursor"], 100)
            self.assertEqual(archive.status()["pending_count"], 1)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 2)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], 1)

    def test_reaction_count_change_does_not_block_new_messages(self):
        original = message(100, reactions=[{"emoji": {"name": "check"}, "count": 1}])
        with source.Archive(self.db) as archive:
            source.poll(archive, lambda before, **_: page(original)
                        if before is None else page())
            replay = message(100, reactions=[{"emoji": {"name": "check"}, "count": 2}])
            result = source.poll(archive, lambda before, **_: page(message(105), replay))
            self.assertEqual(result["read_cursor"], 105)
            self.assertEqual(result["added_events"], 1)
            self.assertEqual(result["pending_count"], 2)
            self.assertEqual(archive.pending(limit=2)["events"][0]["reactions"][0]["count"], 1)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 3)

    def test_pending_includes_validated_source_reference(self):
        with source.Archive(self.db) as archive:
            source.poll(archive, lambda before, **_: page(message(100))
                        if before is None else page())
            event = archive.pending()["events"][0]
            self.assertEqual(event["source_url"],
                             f"https://discord.com/channels/{GUILD}/{CHANNEL}/100")
            self.assertEqual(event["author"]["id"], "123456789012345678")
            self.assertEqual(event["timestamp"], "2026-01-01T00:00:00.000000+00:00")

    def test_reader_uses_only_fixed_get_and_bounded_network(self):
        requests = []

        class Response:
            status = 200

            def __init__(self, request):
                self.request = request
                self.stream = io.BytesIO(page(message(10)))

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def geturl(self):
                return self.request.full_url

            def read(self, size):
                return self.stream.read(size)

        class Opener:
            def open(self, request, timeout):
                requests.append((request, timeout))
                return Response(request)

        reader = source.DiscordReader("synthetic-token", opener=Opener(), monotonic=lambda: 10)
        self.assertEqual(reader.fetch(None, deadline=15), page(message(10)))
        self.assertEqual(reader.fetch(10, deadline=15), page(message(10)))
        request, timeout = requests[1]
        self.assertEqual(request.full_url,
                         f"https://discord.com/api/v10/channels/{CHANNEL}/messages?limit=100&before=10")
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        self.assertEqual(request.get_header("Authorization"), "Bot synthetic-token")
        self.assertEqual(request.get_header("User-agent"),
                         "DiscordBot (https://github.com/NousResearch/hermes-agent, 1.0)")
        self.assertEqual(request.get_header("Accept"), "application/json")
        self.assertEqual(timeout, 5)
        self.assertEqual(requests[0][0].full_url,
                         f"https://discord.com/api/v10/channels/{CHANNEL}/messages?limit=100")
        for cursor in (-1, True, 1.0, "10", 0):
            with self.subTest(cursor=cursor), self.assertRaises(source.SourceError):
                reader.fetch(cursor, deadline=15)
        with self.assertRaises(source.SourceError):
            reader.fetch(None, deadline=10)
        self.assertEqual(len(requests), 2)

    def test_reader_rejects_redirects_http_errors_and_bad_tokens(self):
        for token in (None, "", "bad\r\nheader", "bad token"):
            with self.subTest(token=token), self.assertRaises(source.SourceError):
                source.DiscordReader(token)
        for code in (301, 302, 303, 307, 308):
            calls = []

            class RedirectHTTPS(urllib.request.HTTPSHandler):
                def https_open(self, request, calls=calls, code=code):
                    calls.append(request)
                    headers = Message()
                    headers["Location"] = "https://evil.invalid/steal"
                    response = urllib.response.addinfourl(
                        io.BytesIO(b"private"), headers, request.full_url, code)
                    response.msg = "Redirect"
                    return response

            opener = urllib.request.build_opener(source.NoRedirect(), RedirectHTTPS())
            reader = source.DiscordReader("synthetic-secret", opener=opener,
                                          monotonic=lambda: 0)
            with self.subTest(code=code), self.assertRaises(source.SourceError) as error:
                reader.fetch(None, deadline=5)
            self.assertNotIn("synthetic-secret", str(error.exception))
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0].get_method(), "GET")
        for code in (403, 429):
            class HttpErrorOpener:
                def open(self, request, timeout, code=code):
                    raise urllib.error.HTTPError(request.full_url, code, "private secret", {}, None)

            reader = source.DiscordReader("synthetic-secret", opener=HttpErrorOpener(),
                                          monotonic=lambda: 0)
            with self.subTest(code=code), self.assertRaisesRegex(source.SourceError,
                                                                 f"HTTP {code}") as error:
                reader.fetch(None, deadline=5)
            self.assertNotIn("synthetic-secret", str(error.exception))

    def test_poll_interrupts_blocked_network_with_total_deadline(self):
        def blocked(before, *, deadline):
            time.sleep(0.4)
            return page(message(2))

        with source.Archive(self.db) as archive:
            started = time.monotonic()
            with self.assertRaisesRegex(source.SourceError, "deadline"):
                source.poll(archive, blocked, total_seconds=0.05)
            self.assertLess(time.monotonic() - started, 0.3)
            self.assertEqual(archive.status()["read_cursor"], 0)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 0)

    def test_monitor_retries_unchanged_backlog_without_ack(self):
        with source.Archive(self.db) as archive:
            self.assertEqual(archive.change_token(now=10, retry_seconds=60), "WATCHER_IDLE")
            source.poll(archive, lambda before, **_: page(message(100))
                        if before is None else page())
            first = archive.change_token(now=10, retry_seconds=60)
            self.assertEqual(first,
                             f"WATCHER_WAKE channel={CHANNEL} pending=1 cursor=100 generation=1")
        with source.Archive(self.db) as archive:
            self.assertEqual(archive.change_token(now=69, retry_seconds=60), "WATCHER_IDLE")
            self.assertIn("generation=2", archive.change_token(now=70, retry_seconds=60))
            archive.ack(100)
            self.assertEqual(archive.change_token(now=1000, retry_seconds=60), "WATCHER_IDLE")

    def test_cli_supports_in_process_token_and_machine_readable_commands(self):
        from swarm_forensics.watcher import discord_cli

        def run(*args, **injections):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = discord_cli.main(["--db", str(self.db), *args], **injections)
            return code, out.getvalue(), err.getvalue()

        calls = []

        def fetch(before, *, deadline):
            calls.append(before)
            return page(message(10)) if before is None else page()

        code, output, errors = run("poll", fetch=fetch)
        self.assertEqual(code, 0, errors)
        self.assertEqual(json.loads(output)["added_events"], 1)
        self.assertEqual(calls, [None, 10])
        code, output, errors = run("pending", "--limit", "1")
        self.assertEqual(json.loads(output)["next_cursor"], 10)
        self.assertEqual(run("status")[0], 0)
        code, output, errors = run("ack", "--cursor", "10")
        self.assertEqual(json.loads(output)["processed_cursor"], 10)
        code, output, errors = run("monitor", token="synthetic-token", fetch=fetch,
                                   now=lambda: 100)
        self.assertEqual((code, output), (0, "WATCHER_IDLE\n"), errors)
        self.assertEqual(run("pending")[0], 0)

    def test_cli_uses_injected_token_without_environment_or_argv_secret(self):
        from swarm_forensics.watcher import discord_cli

        seen = []

        class FakeReader:
            def __init__(self, token):
                seen.append(token)

            def fetch(self, before, *, deadline):
                return page()

        out, err = io.StringIO(), io.StringIO()
        with (patch.object(discord_cli, "DiscordReader", FakeReader),
              patch.dict("os.environ", {"DISCORD_BOT_TOKEN": "synthetic-wrong"}, clear=True),
              contextlib.redirect_stdout(out), contextlib.redirect_stderr(err)):
            code = discord_cli.main(["--db", str(self.db), "poll"],
                                    token="synthetic-scoped")
        self.assertEqual(code, 0, err.getvalue())
        self.assertEqual(seen, ["synthetic-scoped"])
        self.assertNotIn("synthetic-scoped", out.getvalue() + err.getvalue())
        self.assertEqual(json.loads(out.getvalue())["caught_up"], True)

    def test_cli_monitor_failure_keeps_backlog_and_emits_retry_token(self):
        from swarm_forensics.watcher import discord_cli

        with source.Archive(self.db) as archive:
            source.poll(archive, lambda before, **_: page(message(100))
                        if before is None else page())

        def failed(before, *, deadline):
            raise source.SourceError("synthetic HTTP 429")

        def tick(now):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = discord_cli.main(["--db", str(self.db), "monitor",
                                         "--retry-seconds", "60"],
                                        fetch=failed, now=lambda: now)
            self.assertEqual(code, 1)
            self.assertIn("429", err.getvalue())
            return out.getvalue().strip()

        self.assertIn("generation=1", tick(10))
        self.assertEqual(tick(11), "WATCHER_IDLE")
        self.assertIn("generation=2", tick(70))
        with source.Archive(self.db) as archive:
            self.assertEqual(archive.status()["processed_cursor"], 0)

    def test_archive_insert_failure_rolls_back_page_events_and_scan(self):
        with source.Archive(self.db) as archive:
            archive.connection.execute("""
                CREATE TRIGGER fail_page BEFORE INSERT ON pages
                BEGIN SELECT RAISE(ABORT, 'synthetic disk failure'); END
            """)
            with self.assertRaises(source.sqlite3.DatabaseError):
                archive.capture(page(message(20)), before=None, captured_at=10)
            self.assertEqual(archive.status()["scan_before"], None)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM events").fetchone()[0], 0)
            archive.connection.execute("DROP TRIGGER fail_page")
            self.assertEqual(archive.capture(page(message(20)), before=None, captured_at=11), 1)

    def test_nonadvancing_resume_page_preserves_partial_scan(self):
        with source.Archive(self.db) as archive:
            archive.capture(page(message(20)), before=None, captured_at=10)
            with self.assertRaisesRegex(source.SourceError, "nonadvancing"):
                archive.capture(page(message(20)), before=20, captured_at=11)
            self.assertEqual(archive.status()["scan_before"], 20)
            self.assertEqual(archive.status()["read_cursor"], 0)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 1)

    def test_archive_creates_private_source_files(self):
        with source.Archive(self.db) as archive:
            archive.capture(page(message(20)), before=None, captured_at=10)
        self.assertEqual(stat.S_IMODE(os.stat(self.db.parent).st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(os.stat(self.db).st_mode), 0o600)

    def test_existing_archive_directory_is_made_private(self):
        self.db.parent.chmod(0o755)
        with source.Archive(self.db):
            pass
        self.assertEqual(stat.S_IMODE(os.stat(self.db.parent).st_mode), 0o700)

    def test_later_http_failure_keeps_partial_pages_resumable(self):
        calls = []

        def failing(before, *, deadline):
            calls.append(before)
            if before is not None:
                raise source.SourceError("Discord HTTP 403")
            return page(message(30), message(20))

        with source.Archive(self.db) as archive:
            with self.assertRaisesRegex(source.SourceError, "403"):
                source.poll(archive, failing)
            self.assertEqual(archive.status()["scan_before"], 20)
            self.assertTrue(archive.status()["gap"])
            self.assertEqual(archive.status()["read_cursor"], 0)
            self.assertEqual(archive.connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 1)
        with source.Archive(self.db) as archive:
            result = source.poll(archive, lambda before, **_: page())
            self.assertEqual(result["read_cursor"], 30)
            self.assertEqual(result["pending_count"], 2)
            self.assertEqual(result["coverage_start"], 20)
        self.assertEqual(calls, [None, 20])

    def test_monitor_missing_credential_still_signals_saved_backlog(self):
        from swarm_forensics.watcher import discord_cli

        with source.Archive(self.db) as archive:
            source.poll(archive, lambda before, **_: page(message(100))
                        if before is None else page())
        out, err = io.StringIO(), io.StringIO()
        with (patch.dict("os.environ", {}, clear=True),
              contextlib.redirect_stdout(out), contextlib.redirect_stderr(err)):
            code = discord_cli.main(["--db", str(self.db), "monitor"], now=lambda: 10)
        self.assertEqual(code, 1)
        self.assertIn("missing or invalid", err.getvalue())
        self.assertTrue(out.getvalue().startswith("WATCHER_WAKE "))

    def test_cli_default_archive_is_repo_private_channel_path(self):
        from swarm_forensics.watcher import discord_cli

        root = Path(__file__).resolve().parents[3]
        self.assertEqual(discord_cli.DEFAULT_DB,
                         root / "data/raw/discord" / CHANNEL / "source.sqlite")
        self.assertTrue(discord_cli.DEFAULT_DB.is_absolute())

    def test_ack_requires_acquired_event_and_never_regresses(self):
        with source.Archive(self.db) as archive:
            source.poll(archive, lambda before, **_: page(message(9), message(7))
                        if before is None else page())
            for cursor in (9, 8, -1, True, 1.5):
                if cursor == 9:
                    continue
                with self.subTest(cursor=cursor), self.assertRaises(source.SourceError):
                    archive.ack(cursor)
            archive.ack(7)
            with self.assertRaises(source.SourceError):
                archive.ack(0)
            archive.ack(9)
            archive.ack(9)
            self.assertEqual(archive.status()["pending_count"], 0)


if __name__ == "__main__":
    unittest.main()
