"""Persist raw source pages and separate acquisition from analysis."""

import json
import math
import signal
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path

ORIGIN = "https://multi.fairystack.com"
SESSION = "ca8ffac066a4"
MAX_PAGE_BYTES = 2 * 1024 * 1024
MAX_PAGE_EVENTS = 1000
MAX_CURSOR = 2**63 - 1


class SourceError(ValueError):
    """Reject unsafe or inconsistent source data."""


def integer(value, minimum=0):
    return type(value) is int and minimum <= value <= MAX_CURSOR


def unix_time(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SourceError("duplicate JSON key")
        result[key] = value
    return result


def decode_page(raw, after):
    if not isinstance(raw, bytes) or len(raw) > MAX_PAGE_BYTES:
        raise SourceError("page exceeds the byte limit")
    try:
        page = json.loads(raw, object_pairs_hook=unique_object)
        json.dumps(page, allow_nan=False)
    except (ValueError, UnicodeError, RecursionError):
        raise SourceError("invalid source JSON") from None
    if not isinstance(page, dict):
        raise SourceError("page must be a mapping")
    if page.get("session_id") != SESSION or page.get("access_mode") != "conversation":
        raise SourceError("wrong session or access mode")
    cursor = page.get("next_cursor")
    if (not integer(after) or not integer(cursor) or cursor < after
            or type(page.get("has_more")) is not bool
            or (page["has_more"] and cursor == after)):
        raise SourceError("nonadvancing or invalid source cursor")
    participant = page.get("participant")
    if not isinstance(participant, dict) or not unix_time(participant.get("expires_at")):
        raise SourceError("missing or invalid participant lease")
    events = page.get("events")
    if not isinstance(events, list) or len(events) > MAX_PAGE_EVENTS:
        raise SourceError("invalid or oversized event page")
    seen = set()
    for event in events:
        if (not isinstance(event, dict) or not integer(event.get("seq"), 1)
                or event["seq"] > cursor or event["seq"] in seen
                or not unix_time(event.get("at"))
                or not isinstance(event.get("author"), dict)
                or not isinstance(event.get("kind"), str)
                or not isinstance(event.get("text"), str)):
            raise SourceError("invalid source event")
        seen.add(event["seq"])
    return page


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SourceError("redirect rejected")


class PeerReader:
    def __init__(self, config, *, opener=None, monotonic=time.monotonic):
        if not isinstance(config, dict) or config.get("origin") != ORIGIN:
            raise SourceError("private configuration has the wrong origin")
        token = config.get("token")
        if (not isinstance(token, str) or not token or not token.isascii()
                or any(ord(char) <= 32 or ord(char) >= 127 for char in token)):
            raise SourceError("private configuration has an invalid token")
        self.token = token
        self.opener = opener or urllib.request.build_opener(NoRedirect())
        self.monotonic = monotonic

    def fetch(self, after, *, deadline):
        if not integer(after):
            raise SourceError("invalid request cursor")
        remaining = deadline - self.monotonic()
        if remaining <= 0:
            raise SourceError("poll deadline reached")
        request = urllib.request.Request(
            ORIGIN + "/api/external-agents/session?after=" + str(after),
            method="GET", headers={"X-FairyStack-Agent-Token": self.token})
        try:
            response = self.opener.open(request, timeout=min(10, remaining))
        except urllib.error.HTTPError as error:
            code = error.code
            error.close()
            raise SourceError(f"HTTP {code}") from None
        except (OSError, urllib.error.URLError, ValueError):
            raise SourceError("peer request failed") from None
        with response:
            if response.geturl() != request.full_url or response.status != 200:
                raise SourceError("unexpected response route or status")
            chunks = []
            size = 0
            while True:
                if self.monotonic() >= deadline:
                    raise SourceError("poll deadline reached")
                chunk = response.read1(min(65536, MAX_PAGE_BYTES + 1 - size))
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_PAGE_BYTES:
                    raise SourceError("page exceeds the byte limit")
                chunks.append(chunk)
        if self.monotonic() >= deadline:
            raise SourceError("poll deadline reached")
        return b"".join(chunks)


class Archive:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS state (
                session_id TEXT PRIMARY KEY,
                read_cursor INTEGER NOT NULL DEFAULT 0,
                processed_cursor INTEGER NOT NULL DEFAULT 0,
                lease_expires_at REAL,
                wake_fingerprint TEXT,
                retry_at REAL,
                wake_generation INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                after_cursor INTEGER NOT NULL,
                next_cursor INTEGER NOT NULL,
                captured_at REAL NOT NULL,
                payload BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                session_id TEXT NOT NULL,
                seq INTEGER NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (session_id, seq)
            );
        """)
        with self.connection:
            self.connection.execute("INSERT OR IGNORE INTO state(session_id) VALUES (?)", (SESSION,))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.connection.close()

    def capture(self, raw, *, after, captured_at):
        page = decode_page(raw, after)
        added = 0
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            if self.status()["read_cursor"] != after:
                raise SourceError("stale acquisition cursor")
            for event in page["events"]:
                payload = json.dumps(event, sort_keys=True, ensure_ascii=False, allow_nan=False)
                old = self.connection.execute(
                    "SELECT payload FROM events WHERE session_id=? AND seq=?",
                    (SESSION, event["seq"])).fetchone()
                if old is not None:
                    if old[0] != payload:
                        raise SourceError("changed source payload under existing identity")
                    continue
                if event["seq"] <= after:
                    raise SourceError("unseen replay below the acquired cursor")
                self.connection.execute("INSERT INTO events VALUES (?,?,?)",
                                        (SESSION, event["seq"], payload))
                added += 1
            self.connection.execute(
                "INSERT INTO pages(after_cursor, next_cursor, captured_at, payload) VALUES(?,?,?,?)",
                (after, page["next_cursor"], captured_at, raw))
            self.connection.execute(
                "UPDATE state SET read_cursor=?, lease_expires_at=? WHERE session_id=?",
                (page["next_cursor"], page["participant"]["expires_at"], SESSION))
        return added

    def status(self):
        read, processed, lease = self.connection.execute(
            "SELECT read_cursor, processed_cursor, lease_expires_at FROM state WHERE session_id=?",
            (SESSION,)
        ).fetchone()
        count = self.connection.execute(
            "SELECT COUNT(*) FROM events WHERE session_id=? AND seq>?", (SESSION, processed)
        ).fetchone()[0]
        return {"session_id": SESSION, "read_cursor": read, "processed_cursor": processed,
                "pending_count": count, "lease_expires_at": lease}

    def pending(self, limit=50):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise SourceError("pending limit must be an integer from 1 through 1000")
        with self.connection:
            self.connection.execute("BEGIN")
            state = self.status()
            rows = self.connection.execute(
                "SELECT payload FROM events WHERE session_id=? AND seq>? ORDER BY seq LIMIT ?",
                (SESSION, state["processed_cursor"], limit + 1)).fetchall()
        events = [json.loads(row[0]) for row in rows[:limit]]
        return {**state, "events": events, "has_more": len(rows) > limit,
                "next_cursor": events[-1]["seq"] if events else state["processed_cursor"]}

    def change_token(self, *, now, retry_seconds=900):
        if (not unix_time(now) or not unix_time(retry_seconds)
                or not 1 <= retry_seconds <= 86400):
            raise SourceError("invalid backlog retry interval")
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            state = self.status()
            if not state["pending_count"]:
                self.connection.execute(
                    "UPDATE state SET wake_fingerprint=NULL, retry_at=NULL WHERE session_id=?",
                    (SESSION,))
                return "WATCHER_IDLE"
            first, last = self.connection.execute(
                "SELECT MIN(seq), MAX(seq) FROM events WHERE session_id=? AND seq>?",
                (SESSION, state["processed_cursor"])).fetchone()
            fingerprint = f"{first}:{last}:{state['pending_count']}"
            old, retry_at, generation = self.connection.execute(
                "SELECT wake_fingerprint, retry_at, wake_generation FROM state WHERE session_id=?",
                (SESSION,)).fetchone()
            if old == fingerprint and retry_at is not None and now < retry_at:
                return "WATCHER_IDLE"
            generation += 1
            self.connection.execute(
                "UPDATE state SET wake_fingerprint=?, retry_at=?, wake_generation=? "
                "WHERE session_id=?", (fingerprint, now + retry_seconds, generation, SESSION))
        return (f"WATCHER_WAKE session={SESSION} pending={state['pending_count']} "
                f"cursor={last} generation={generation}")

    def ack(self, cursor):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            state = self.status()
            if (type(cursor) is not int
                    or not state["processed_cursor"] <= cursor <= state["read_cursor"]):
                raise SourceError("ack cursor regresses or exceeds the acquired cursor")
            self.connection.execute("UPDATE state SET processed_cursor=? WHERE session_id=?",
                                    (cursor, SESSION))
        return self.status()


@contextmanager
def request_deadline(seconds):
    if threading.current_thread() is not threading.main_thread():
        raise SourceError("poll requires the main thread")
    if signal.getitimer(signal.ITIMER_REAL)[0]:
        raise SourceError("poll cannot replace an active process timer")
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
    if (not integer(max_pages, 1) or max_pages > 1000 or not unix_time(total_seconds)
            or not 0 < total_seconds <= 300):
        raise SourceError("invalid poll page cap or total deadline")
    deadline = monotonic() + total_seconds
    added = 0
    pages = 0
    caught_up = False
    reason = "page_cap"
    for _ in range(max_pages):
        state = archive.status()
        if state["lease_expires_at"] is not None and now() >= state["lease_expires_at"]:
            raise SourceError("stored participant lease expired")
        if monotonic() >= deadline:
            reason = "deadline"
            break
        with request_deadline(deadline - monotonic()):
            raw = fetch(state["read_cursor"], deadline=deadline)
        if monotonic() >= deadline:
            raise SourceError("poll deadline reached")
        added += archive.capture(raw, after=state["read_cursor"], captured_at=now())
        pages += 1
        if not decode_page(raw, state["read_cursor"])["has_more"]:
            caught_up = True
            reason = "caught_up"
            break
    return {**archive.status(), "pages": pages, "added_events": added,
            "caught_up": caught_up, "stop_reason": reason}
