"""Archive bounded, read-only Discord channel message pages."""

import json
import math
import os
import signal
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

CHANNEL = "1430962817045106792"
GUILD = "1430962816315031654"
MAX_ID = 2**63 - 1
MAX_PAGE_BYTES = 2 * 1024 * 1024
ORIGIN = "https://discord.com"


class SourceError(ValueError):
    """Reject invalid source pages or unsafe archive operations."""


def valid_id(value):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        return False
    try:
        return str(int(value)) == value and 0 < int(value) <= MAX_ID
    except ValueError:
        return False


def valid_timestamp(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except ValueError:
        return False


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SourceError("duplicate JSON key")
        result[key] = value
    return result


def decode_page(raw, before):
    if not isinstance(raw, bytes) or len(raw) > MAX_PAGE_BYTES:
        raise SourceError("page exceeds byte limit")
    try:
        events = json.loads(raw, object_pairs_hook=unique_object)
        json.dumps(events, allow_nan=False)
    except (ValueError, UnicodeError, RecursionError):
        raise SourceError("invalid source JSON") from None
    if not isinstance(events, list) or len(events) > 100:
        raise SourceError("invalid Discord message page")
    previous = before if before is not None else MAX_ID + 1
    for event in events:
        if (not isinstance(event, dict) or not valid_id(event.get("id"))
                or int(event["id"]) >= previous or event.get("channel_id") != CHANNEL
                or not isinstance(event.get("author"), dict)
                or not valid_id(event["author"].get("id"))
                or not valid_timestamp(event.get("timestamp"))
                or not isinstance(event.get("content"), str)):
            raise SourceError("invalid, wrong-channel, or nonadvancing message page")
        previous = int(event["id"])
    return events


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Reject redirects before any authorization header can move."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SourceError("redirect rejected")


class DiscordReader:
    """Use one fixed Discord GET route with bounded response bytes."""

    def __init__(self, token, *, opener=None, monotonic=time.monotonic):
        if (not isinstance(token, str) or not token or not token.isascii()
                or any(ord(char) <= 32 or ord(char) >= 127 for char in token)):
            raise SourceError("missing or invalid Discord credential")
        self._token = token
        self._opener = opener or urllib.request.build_opener(NoRedirect())
        self._monotonic = monotonic

    def fetch(self, before, *, deadline):
        if before is not None and (type(before) is not int or not 0 < before <= MAX_ID):
            raise SourceError("invalid request cursor")
        remaining = deadline - self._monotonic()
        if remaining <= 0:
            raise SourceError("poll deadline reached")
        url = f"{ORIGIN}/api/v10/channels/{CHANNEL}/messages?limit=100"
        if before is not None:
            url += f"&before={before}"
        request = urllib.request.Request(
            url, method="GET",
            headers={"Authorization": f"Bot {self._token}",
                     "User-Agent": "DiscordBot (https://github.com/NousResearch/hermes-agent, 1.0)",
                     "Accept": "application/json"})
        try:
            response = self._opener.open(request, timeout=min(10, remaining))
        except urllib.error.HTTPError as error:
            code = error.code
            error.close()
            raise SourceError(f"Discord HTTP {code}") from None
        except SourceError:
            raise
        except (OSError, ValueError):
            raise SourceError("Discord GET failed") from None
        with response:
            if response.geturl() != url or response.status != 200:
                raise SourceError("unexpected Discord response route or status")
            try:
                raw = response.read(MAX_PAGE_BYTES + 1)
            except (OSError, ValueError):
                raise SourceError("Discord GET failed") from None
        if len(raw) > MAX_PAGE_BYTES:
            raise SourceError("page exceeds byte limit")
        if self._monotonic() >= deadline:
            raise SourceError("poll deadline reached")
        return raw


class Archive:
    """Keep acquired pages separate from acknowledged events."""

    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        path.parent.chmod(0o700)
        if path.is_symlink():
            raise SourceError("archive path must not be a symlink")
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(fd)
        path.chmod(0o600)
        self.connection = sqlite3.connect(path)
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS state (
                channel_id TEXT PRIMARY KEY,
                read_cursor INTEGER NOT NULL DEFAULT 0,
                processed_cursor INTEGER NOT NULL DEFAULT 0,
                coverage_start INTEGER,
                scan_before INTEGER,
                scan_high INTEGER,
                wake_fingerprint TEXT,
                retry_at REAL,
                wake_generation INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                before_cursor INTEGER,
                captured_at REAL NOT NULL,
                payload BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                channel_id TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (channel_id, message_id)
            );
        """)
        with self.connection:
            self.connection.execute("INSERT OR IGNORE INTO state(channel_id) VALUES (?)", (CHANNEL,))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.connection.close()

    def status(self):
        read, processed, coverage, before, high = self.connection.execute(
            "SELECT read_cursor, processed_cursor, coverage_start, scan_before, scan_high "
            "FROM state WHERE channel_id=?", (CHANNEL,)).fetchone()
        count = self.connection.execute(
            "SELECT COUNT(*) FROM events WHERE channel_id=? AND message_id>? "
            "AND message_id<=?", (CHANNEL, processed, read)).fetchone()[0]
        source_count = self.connection.execute(
            "SELECT COUNT(*) FROM events WHERE channel_id=?", (CHANNEL,)).fetchone()[0]
        captured_at = self.connection.execute(
            "SELECT MAX(captured_at) FROM pages").fetchone()[0]
        return {"guild_id": GUILD, "channel_id": CHANNEL, "read_cursor": read,
                "processed_cursor": processed, "pending_count": count,
                "source_count": source_count,
                "last_capture_at": datetime.fromtimestamp(captured_at, timezone.utc).isoformat()
                if captured_at is not None else None,
                "scan_before": before, "scan_high": high,
                "coverage_start": coverage, "gap": before is not None,
                "threads_included": False}

    def capture(self, raw, *, before, captured_at):
        events = decode_page(raw, before)
        if (type(captured_at) not in (float, int) or not math.isfinite(captured_at)
                or captured_at < 0):
            raise SourceError("invalid capture time")
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            state = self.status()
            if before != state["scan_before"]:
                raise SourceError("stale scan cursor")
            added = 0
            for event in events:
                identifier = int(event["id"])
                payload = json.dumps(event, sort_keys=True, ensure_ascii=False, allow_nan=False)
                old = self.connection.execute(
                    "SELECT payload FROM events WHERE channel_id=? AND message_id=?",
                    (CHANNEL, identifier)).fetchone()
                if old:
                    recorded = json.loads(old[0])
                    stable = {key: value for key, value in event.items() if key != "reactions"}
                    prior = {key: value for key, value in recorded.items() if key != "reactions"}
                    if stable != prior:
                        raise SourceError("changed source payload under existing identity")
                    continue
                if state["read_cursor"] and identifier <= state["read_cursor"]:
                    raise SourceError("unseen message below acquired cursor")
                self.connection.execute("INSERT INTO events VALUES (?,?,?)",
                                        (CHANNEL, identifier, payload))
                added += 1
            self.connection.execute("INSERT INTO pages(before_cursor,captured_at,payload) "
                                    "VALUES(?,?,?)", (before, captured_at, raw))
            high = state["scan_high"]
            if events and high is None:
                high = int(events[0]["id"])
            earliest = int(events[-1]["id"]) if events else before
            complete = not events or (state["read_cursor"] and earliest <= state["read_cursor"])
            if complete:
                coverage = state["coverage_start"]
                if coverage is None and before is not None:
                    coverage = earliest
                self.connection.execute(
                    "UPDATE state SET read_cursor=?, coverage_start=?, scan_before=NULL, "
                    "scan_high=NULL WHERE channel_id=?",
                    (high or state["read_cursor"], coverage, CHANNEL))
            else:
                self.connection.execute(
                    "UPDATE state SET scan_before=?, scan_high=? WHERE channel_id=?",
                    (earliest, high, CHANNEL))
        return added

    def pending(self, limit=50):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise SourceError("pending limit must be 1 through 1000")
        with self.connection:
            self.connection.execute("BEGIN")
            state = self.status()
            rows = self.connection.execute(
                "SELECT payload FROM events WHERE channel_id=? AND message_id>? "
                "AND message_id<=? ORDER BY message_id LIMIT ?",
                (CHANNEL, state["processed_cursor"], state["read_cursor"], limit + 1)).fetchall()
        events = [json.loads(row[0]) for row in rows[:limit]]
        for event in events:
            event["source_url"] = (
                f"https://discord.com/channels/{GUILD}/{CHANNEL}/{event['id']}")
        return {**state, "events": events, "has_more": len(rows) > limit,
                "next_cursor": int(events[-1]["id"]) if events else state["processed_cursor"]}

    def audit(self, events_path):
        """Verify private ledger provenance without exposing message content."""
        seen = set()
        with Path(events_path).open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    record = json.loads(line, object_pairs_hook=unique_object)
                except (ValueError, UnicodeError):
                    raise SourceError("invalid private event JSON") from None
                if not isinstance(record, dict):
                    raise SourceError("invalid private event record")
                source_id = str(record.get("source_message_id", ""))
                event_id = record.get("id", record.get("event_id"))
                expected_id = f"discord:{CHANNEL}:{source_id}:{record.get('type', '')}"
                if (not valid_id(source_id) or event_id != expected_id or event_id in seen
                        or record.get("channel_id") != CHANNEL
                        or record.get("guild_id") != GUILD):
                    raise SourceError("private event provenance mismatch")
                seen.add(event_id)
                source = self.connection.execute(
                    "SELECT payload FROM events WHERE channel_id=? AND message_id=?",
                    (CHANNEL, int(source_id))).fetchone()
                if source is None:
                    raise SourceError("private event provenance missing source")
                original = json.loads(source[0])
                if (record.get("author_id") != original["author"]["id"]
                        or record.get("timestamp") != original["timestamp"]
                        or record.get("source_quote") != original["content"]
                        or record.get("source_url") !=
                        f"https://discord.com/channels/{GUILD}/{CHANNEL}/{source_id}"):
                    raise SourceError("private event provenance mismatch")
                related = record.get("source_message_ids", [source_id])
                if not isinstance(related, list) or source_id not in [str(x) for x in related]:
                    raise SourceError("private event provenance invalid links")
                for linked in related:
                    if not valid_id(str(linked)) or self.connection.execute(
                        "SELECT 1 FROM events WHERE channel_id=? AND message_id=?",
                        (CHANNEL, int(linked))).fetchone() is None:
                        raise SourceError("private event provenance missing related source")
        return {**self.status(), "verified_event_count": len(seen)}

    def change_token(self, *, now, retry_seconds=900):
        if (type(now) not in (float, int) or not math.isfinite(now) or now < 0
                or type(retry_seconds) not in (float, int)
                or not math.isfinite(retry_seconds)
                or not 1 <= retry_seconds <= 86400):
            raise SourceError("invalid backlog retry interval")
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            state = self.status()
            if not state["pending_count"]:
                self.connection.execute(
                    "UPDATE state SET wake_fingerprint=NULL, retry_at=NULL WHERE channel_id=?",
                    (CHANNEL,))
                return "WATCHER_IDLE"
            first, last = self.connection.execute(
                "SELECT MIN(message_id), MAX(message_id) FROM events WHERE channel_id=? "
                "AND message_id>? AND message_id<=?",
                (CHANNEL, state["processed_cursor"], state["read_cursor"])).fetchone()
            fingerprint = f"{first}:{last}:{state['pending_count']}"
            old, retry_at, generation = self.connection.execute(
                "SELECT wake_fingerprint, retry_at, wake_generation FROM state "
                "WHERE channel_id=?", (CHANNEL,)).fetchone()
            if old == fingerprint and retry_at is not None and now < retry_at:
                return "WATCHER_IDLE"
            generation += 1
            self.connection.execute(
                "UPDATE state SET wake_fingerprint=?, retry_at=?, wake_generation=? "
                "WHERE channel_id=?", (fingerprint, now + retry_seconds, generation, CHANNEL))
        return (f"WATCHER_WAKE channel={CHANNEL} pending={state['pending_count']} "
                f"cursor={last} generation={generation}")

    def ack(self, cursor):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            state = self.status()
            if (type(cursor) is not int or cursor < state["processed_cursor"]
                    or cursor > state["read_cursor"]):
                raise SourceError("ack cursor regresses or exceeds acquired cursor")
            if cursor not in (0, state["processed_cursor"]) and not self.connection.execute(
                "SELECT 1 FROM events WHERE channel_id=? AND message_id=?",
                (CHANNEL, cursor)).fetchone():
                raise SourceError("ack cursor must name an acquired message")
            self.connection.execute("UPDATE state SET processed_cursor=? WHERE channel_id=?",
                                    (cursor, CHANNEL))
        return self.status()


@contextmanager
def request_deadline(seconds):
    if threading.current_thread() is not threading.main_thread():
        raise SourceError("poll requires the main thread")
    if signal.getitimer(signal.ITIMER_REAL)[0]:
        raise SourceError("poll cannot replace an active timer")
    previous = signal.getsignal(signal.SIGALRM)

    def expired(signum, frame):
        raise SourceError("poll deadline reached")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def poll(archive, fetch, *, max_pages=20, total_seconds=30,
         monotonic=time.monotonic, now=time.time):
    if (type(max_pages) is not int or not 1 <= max_pages <= 1000
            or type(total_seconds) not in (int, float)
            or not math.isfinite(total_seconds) or not 0 < total_seconds <= 300):
        raise SourceError("invalid poll bounds")
    deadline = monotonic() + total_seconds
    pages = added = 0
    reason = "page_cap"
    for _ in range(max_pages):
        if monotonic() >= deadline:
            reason = "deadline"
            break
        before = archive.status()["scan_before"]
        with request_deadline(deadline - monotonic()):
            raw = fetch(before, deadline=deadline)
        if monotonic() >= deadline:
            raise SourceError("poll deadline reached")
        added += archive.capture(raw, before=before, captured_at=now())
        pages += 1
        if archive.status()["scan_before"] is None:
            reason = "caught_up"
            break
    return {**archive.status(), "pages": pages, "added_events": added,
            "caught_up": reason == "caught_up", "stop_reason": reason}
