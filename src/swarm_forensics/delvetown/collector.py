"""Retain bounded public records and private source provenance."""

import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlencode

from .records import SourceError, normalize, timestamp

APPVIEW = "https://api.delve.town"
COLLECTION = "town.delve.feed.post"
MAX_POSTS = 10_000


def canonical(value):
    """Serialize retained source JSON without changing record values."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def private_file(path):
    """Create a new private file without replacing an existing file."""
    return os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                     "w", encoding="utf-8")


def validate_cohort(cohort):
    """Require a fixed, unique, bounded public account cohort."""
    if not isinstance(cohort, list) or not 1 <= len(cohort) <= 45:
        raise SourceError("cohort must contain one through 45 accounts")
    seen = set()
    for actor in cohort:
        if (not isinstance(actor, dict)
                or not re.fullmatch(r"did:plc:[a-z2-7]{24}", actor.get("did", ""))
                or not isinstance(actor.get("handle"), str) or not actor["handle"]
                or actor["did"] in seen):
            raise SourceError("invalid or duplicate cohort account")
        seen.add(actor["did"])


def collect(cohort, dest, *, reader, started_at=None, max_posts=MAX_POSTS):
    """Scan account repositories and retain only the fixed 72-hour window."""
    validate_cohort(cohort)
    if not 1 <= max_posts <= MAX_POSTS:
        raise SourceError("invalid post limit")
    started_at = started_at or datetime.now(timezone.utc)
    cutoff = started_at - timedelta(hours=72)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.mkdir(mode=0o700)
    with private_file(dest / "archive.sqlite"):
        pass
    conn = sqlite3.connect(dest / "archive.sqlite")
    conn.executescript("""
        CREATE TABLE requests(id INTEGER PRIMARY KEY, metadata TEXT NOT NULL);
        CREATE TABLE actors(did TEXT PRIMARY KEY, snapshot TEXT NOT NULL,
                            coverage TEXT NOT NULL, pages INTEGER NOT NULL DEFAULT 0,
                            seen INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE posts(uri TEXT PRIMARY KEY, cid TEXT NOT NULL, did TEXT NOT NULL,
                           raw TEXT NOT NULL, normalized TEXT NOT NULL,
                           source_request INTEGER NOT NULL REFERENCES requests(id));
        CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    """)
    state = {"started_at": started_at.isoformat(), "window_start": cutoff.isoformat(),
             "window_end": started_at.isoformat(), "cohort_accounts": len(cohort),
             "publication": "deferred", "collection": "public_GET_only",
             "raw_format": "selected record JSON; response bodies are hashed, not retained",
             "stop_reason": "finished"}
    conn.execute("INSERT INTO metadata VALUES ('scope', ?)", (canonical(state),))
    for actor in cohort:
        conn.execute("INSERT INTO actors VALUES (?, ?, 'not_attempted', 0, 0)",
                     (actor["did"], canonical(actor)))
    conn.commit()
    post_count = 0
    history_count = 0

    def fetch(url):
        nonlocal history_count
        metadata = None
        try:
            body, metadata = reader.get(url)
        finally:
            history = getattr(reader, "history", [])
            additions = history[history_count:] or ([metadata] if metadata is not None else [])
            history_count = len(history)
            for entry in additions:
                cursor = conn.execute("INSERT INTO requests(metadata) VALUES (?)", (canonical(entry),))
            conn.commit()
        return body, cursor.lastrowid, metadata["received_at"]

    try:
        for actor in cohort:
            did = actor["did"]
            coverage = "complete"
            try:
                profile, profile_ref, _ = fetch(APPVIEW + "/xrpc/town.delve.actor.getProfile?"
                                                + urlencode({"actor": did}))
                if profile.get("did") != did:
                    raise SourceError("profile DID mismatch")
                minimal = {key: profile[key] for key in
                           ("did", "handle", "displayName", "description", "labels", "createdAt")
                           if key in profile}
                minimal["profile_source_request"] = profile_ref
                conn.execute("UPDATE actors SET snapshot=? WHERE did=?", (canonical(minimal), did))
                document, _, _ = fetch("https://plc.directory/" + quote(did, safe=":"))
                if document.get("id") != did:
                    raise SourceError("identity document mismatch")
                services = [service for service in document.get("service", [])
                            if service.get("type") == "AtprotoPersonalDataServer"]
                if len(services) != 1 or not isinstance(services[0].get("serviceEndpoint"), str):
                    raise SourceError("missing or ambiguous account PDS")
                origin = services[0]["serviceEndpoint"].rstrip("/")
                minimal["pds"] = origin
                conn.execute("UPDATE actors SET snapshot=? WHERE did=?", (canonical(minimal), did))
                cursor = None
                cursors = set()
                while True:
                    params = {"repo": did, "collection": COLLECTION, "limit": 100}
                    if cursor:
                        params["cursor"] = cursor
                    page, request_id, captured_at = fetch(origin + "/xrpc/com.atproto.repo.listRecords?"
                                                          + urlencode(params))
                    records = page.get("records")
                    if not isinstance(records, list) or len(records) > 100:
                        raise SourceError("invalid repository page")
                    conn.execute("UPDATE actors SET pages=pages+1, seen=seen+? WHERE did=?",
                                 (len(records), did))
                    for item in records:
                        normalized = normalize(item, did, started_at)
                        when = timestamp(normalized["created_at"])
                        if not cutoff <= when <= started_at:
                            continue
                        normalized["collected_at"] = captured_at
                        normalized["source_request"] = request_id
                        old = conn.execute("SELECT cid, raw FROM posts WHERE uri=?",
                                           (item["uri"],)).fetchone()
                        if old:
                            if old != (item["cid"], canonical(item)):
                                raise SourceError("record changed during capture")
                            continue
                        if post_count >= max_posts:
                            raise SourceError("post_limit")
                        conn.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)",
                                     (item["uri"], item["cid"], did, canonical(item),
                                      canonical(normalized), request_id))
                        post_count += 1
                        if post_count >= max_posts:
                            raise SourceError("post_limit")
                    conn.commit()
                    cursor = page.get("cursor")
                    if not records or not cursor:
                        break
                    if not isinstance(cursor, str) or cursor in cursors:
                        raise SourceError("stalled repository cursor")
                    cursors.add(cursor)
            except SourceError as error:
                coverage = "incomplete: " + str(error)
                if str(error).endswith("_limit"):
                    state["stop_reason"] = str(error)
            conn.execute("UPDATE actors SET coverage=? WHERE did=?", (coverage, did))
            conn.commit()
            if state["stop_reason"] != "finished":
                break
        state["requests"] = reader.requests
        state["body_bytes"] = reader.body_bytes
        conn.execute("UPDATE metadata SET value=? WHERE key='scope'", (canonical(state),))
        conn.commit()
        with private_file(dest / "posts.jsonl") as output:
            for (payload,) in conn.execute("SELECT normalized FROM posts ORDER BY uri"):
                output.write(payload + "\n")
        receipt = dict(state)
        receipt["posts"] = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        receipt["accounts_complete"] = conn.execute(
            "SELECT COUNT(*) FROM actors WHERE coverage='complete'").fetchone()[0]
        receipt["accounts"] = [dict(zip(("did", "profile", "coverage", "pages", "records_seen"), row))
                               for row in conn.execute("SELECT * FROM actors ORDER BY did")]
        for row in receipt["accounts"]:
            row["profile"] = json.loads(row["profile"])
        with private_file(dest / "coverage.json") as output:
            output.write(canonical(receipt) + "\n")
        from .report import export_report

        export_report(dest)
        return {key: value for key, value in receipt.items() if key != "accounts"}
    finally:
        conn.close()
