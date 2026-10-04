"""Verify the public-record pilot with synthetic source records."""

import hashlib
import json
import stat
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from swarm_forensics.delvetown.records import SourceError, normalize

DID = "did:plc:aaaaaaaaaaaaaaaaaaaaaaaa"
URI = f"at://{DID}/town.delve.feed.post/synthetic"
NOW = datetime(2026, 10, 3, 12, tzinfo=timezone.utc)


def record(text="Synthetic coordination fixture.", created="2026-10-02T12:00:00Z"):
    return {"uri": URI, "cid": "bafysynthetic", "value": {
        "$type": "town.delve.feed.post", "text": text, "createdAt": created}}


class RecordTests(unittest.TestCase):
    def test_normalize_preserves_text_and_explicit_references(self):
        item = record()
        item["value"]["reply"] = {"parent": {"uri": URI + "parent", "cid": "parent"},
                                    "root": {"uri": URI + "root", "cid": "root"}}
        item["value"]["facets"] = [{"features": [
            {"$type": "town.delve.richtext.facet#mention", "did": DID},
            {"$type": "town.delve.richtext.facet#link", "uri": "https://example.test/"}]}]
        result = normalize(item, DID, NOW)
        self.assertEqual(result["text"], item["value"]["text"])
        self.assertEqual(result["reply_parent"], URI + "parent")
        self.assertEqual(result["mentions"], [DID])
        self.assertEqual(result["links"], ["https://example.test/"])
        self.assertEqual(result["actor_did"], DID)

    def test_normalize_extracts_quote_and_plain_text_link(self):
        item = record("Synthetic reference: https://example.test/spec")
        item["value"]["embed"] = {"$type": "town.delve.embed.record",
                                    "record": {"uri": URI + "quoted", "cid": "quoted"}}
        result = normalize(item, DID, NOW)
        self.assertEqual(result["quote_uris"], [URI + "quoted"])
        self.assertEqual(result["links"], ["https://example.test/spec"])

    def test_malformed_reference_fields_raise_a_source_error(self):
        item = record()
        item["value"]["facets"] = [{"features": [{"$type": 12, "did": ["invalid"]}]}]
        with self.assertRaises(SourceError):
            normalize(item, DID, NOW)


class FixtureReader:
    def __init__(self, text=None):
        self.requests = 0
        self.body_bytes = 0
        self.text = text

    def get(self, url):
        self.requests += 1
        if "getProfile" in url:
            body = {"did": DID, "handle": "synthetic.example", "labels": [],
                    "description": "Synthetic account fixture."}
        elif "plc.directory" in url:
            body = {"id": DID, "service": [{"type": "AtprotoPersonalDataServer",
                                           "serviceEndpoint": "https://pds.example"}]}
        elif "cursor=" in url:
            second = record()
            second["uri"] += "second"
            second["value"]["reply"] = {"parent": {"uri": URI, "cid": "bafysynthetic"},
                                         "root": {"uri": URI + "missing", "cid": "missing"}}
            body = {"records": [second]}
        else:
            body = {"records": [record(created="2026-09-01T12:00:00Z"), record()],
                    "cursor": "synthetic-cursor"}
        if self.text is not None:
            for item in body.get("records", []):
                item["value"]["text"] = self.text
        raw = json.dumps(body).encode()
        self.body_bytes += len(raw)
        return body, {"url": url, "method": "GET", "status": 200,
                      "received_at": NOW.isoformat(), "body_bytes": len(raw),
                      "body_sha256": hashlib.sha256(raw).hexdigest(), "headers": {}}


class PilotTests(unittest.TestCase):
    def test_collect_filters_by_timestamp_and_preserves_private_provenance(self):
        from swarm_forensics.delvetown.collector import collect

        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "pilot"
            receipt = collect([{"did": DID, "handle": "synthetic.example"}], dest,
                              reader=FixtureReader(), started_at=NOW)
            self.assertEqual(receipt["posts"], 2)
            self.assertEqual(receipt["accounts_complete"], 1)
            self.assertEqual(receipt["requests"], 4)
            rows = [json.loads(line) for line in (dest / "posts.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row["source_request"] for row in rows))
            self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)
            self.assertTrue(all(stat.S_IMODE(path.stat().st_mode) == 0o600
                                for path in dest.iterdir()))

    def test_post_limit_stops_before_the_next_request(self):
        from swarm_forensics.delvetown.collector import collect

        with tempfile.TemporaryDirectory() as parent:
            reader = FixtureReader()
            result = collect([{"did": DID, "handle": "synthetic.example"}],
                             Path(parent) / "pilot", reader=reader, started_at=NOW, max_posts=1)
            self.assertEqual(result["posts"], 1)
            self.assertEqual(result["stop_reason"], "post_limit")
            self.assertEqual(reader.requests, 3)

    def test_audit_verifies_sources_edges_and_rejects_modified_export(self):
        from swarm_forensics.delvetown.collector import collect
        from swarm_forensics.delvetown.report import audit

        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "pilot"
            collect([{"did": DID, "handle": "synthetic.example"}], dest,
                    reader=FixtureReader(), started_at=NOW)
            result = audit(dest)
            self.assertEqual(result["posts"], 2)
            self.assertEqual(result["edges"], 2)
            self.assertEqual(result["unresolved_post_references"], 1)
            rows = [json.loads(line) for line in (dest / "posts.jsonl").read_text().splitlines()]
            rows[0]["text"] = "Changed synthetic export."
            (dest / "posts.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")
            with self.assertRaises(SourceError):
                audit(dest)

    def test_cli_rejects_output_outside_the_ignored_source_directory(self):
        from swarm_forensics.delvetown.__main__ import destination

        with self.assertRaises(SourceError):
            destination(Path.home() / "public-delvetown-export")

    def test_request_budget_preserves_auditable_partial_coverage(self):
        from swarm_forensics.delvetown.collector import collect
        from swarm_forensics.delvetown.report import audit
        from swarm_forensics.delvetown.transport import Reader

        fixture = FixtureReader()
        now = [0.0]

        def network(url, timeout, limit):
            body, _metadata = fixture.get(url)
            return 200, {}, json.dumps(body).encode()

        reader = Reader([DID], max_requests=2, clock=lambda: now[0], network=network,
                        sleep=lambda seconds: now.__setitem__(0, now[0] + seconds))
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "pilot"
            collect([{"did": DID, "handle": "synthetic.example"}], dest,
                    reader=reader, started_at=NOW)
            result = audit(dest)
            self.assertEqual(result["requests"], 2)
            self.assertEqual(result["posts"], 0)
            self.assertEqual(result["accounts_complete"], 0)
            self.assertEqual(result["stop_reason"], "request_limit")

    def test_existing_archive_is_never_overwritten(self):
        from swarm_forensics.delvetown.collector import collect

        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "pilot"
            dest.mkdir()
            with self.assertRaises(FileExistsError):
                collect([{"did": DID, "handle": "synthetic.example"}], dest,
                        reader=FixtureReader(), started_at=NOW)

    def test_inspection_bounds_thread_excerpts_and_labels_missing_roots(self):
        from swarm_forensics.delvetown.collector import collect
        from swarm_forensics.delvetown.report import inspect

        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "pilot"
            collect([{"did": DID, "handle": "synthetic.example"}], dest,
                    reader=FixtureReader(), started_at=NOW)
            result = inspect(dest, limit=2, excerpt_chars=12)
            self.assertEqual(result["active_accounts"][0]["posts"], 2)
            self.assertEqual(len(result["threads"]), 2)
            self.assertTrue(any(not row["root_in_archive"] for row in result["threads"]))
            self.assertTrue(all(len(row["excerpt"]) <= 12 for row in result["threads"]))

    def test_record_view_preserves_long_text_and_explicit_provenance(self):
        from swarm_forensics.delvetown.collector import collect
        from swarm_forensics.delvetown.report import record_view

        text = "Synthetic long record. " * 300
        with tempfile.TemporaryDirectory() as parent:
            dest = Path(parent) / "pilot"
            collect([{"did": DID, "handle": "synthetic.example"}], dest,
                    reader=FixtureReader(text=text), started_at=NOW)
            result = record_view(dest, URI)
            self.assertEqual(result["post"]["text"], text)
            self.assertEqual(result["source_handle"], "synthetic.example")
            self.assertEqual(result["source_request"]["method"], "GET")
            with self.assertRaises(SourceError):
                record_view(dest, URI + "absent")


class ReaderTests(unittest.TestCase):
    def test_public_reader_enforces_routes_request_budget_and_spacing(self):
        from swarm_forensics.delvetown.transport import Reader

        now = [0.0]
        calls = []

        def network(url, timeout, limit):
            calls.append((url, now[0], limit))
            return 200, {}, b'{"records": []}'

        reader = Reader([DID], max_requests=2, clock=lambda: now[0],
                        sleep=lambda seconds: now.__setitem__(0, now[0] + seconds),
                        network=network)
        route = ("https://pds.example/xrpc/com.atproto.repo.listRecords?"
                 f"repo={DID}&collection=town.delve.feed.post&limit=100")
        reader.get(route)
        reader.get(route)
        self.assertGreaterEqual(calls[1][1] - calls[0][1], 1)
        with self.assertRaisesRegex(SourceError, "request_limit"):
            reader.get(route)
        self.assertEqual(len(calls), 2)
        unsafe = Reader([DID], network=network)
        with self.assertRaises(SourceError):
            unsafe.get(route.replace("town.delve.feed.post", "app.bsky.graph.follow"))
        with self.assertRaises(SourceError):
            unsafe.get("https://pds.example/xrpc/com.atproto.server.getSession")
        self.assertEqual(len(calls), 2)

    def test_reader_rejects_nonpublic_dns_destinations(self):
        from swarm_forensics.delvetown.transport import safe_addresses

        with self.assertRaises(SourceError):
            safe_addresses("synthetic.example", resolver=lambda host, port: [
                (2, 1, 6, "", ("127.0.0.1", 443))])

    def test_reader_honors_retry_after_and_rejects_redirects(self):
        from swarm_forensics.delvetown.transport import Reader

        now = [0.0]
        starts = []

        def network(url, timeout, limit):
            starts.append(now[0])
            if len(starts) == 1:
                return 429, {"retry-after": "2"}, b'{"error":"synthetic rate limit"}'
            return 200, {}, b'{"ok":true}'

        url = "https://api.delve.town/xrpc/town.delve.actor.getProfile?actor=" + DID
        reader = Reader([DID], clock=lambda: now[0],
                        sleep=lambda seconds: now.__setitem__(0, now[0] + seconds), network=network)
        reader.get(url)
        self.assertGreaterEqual(starts[1] - starts[0], 2)
        self.assertEqual(len(reader.history), 2)
        redirect = Reader([DID], network=lambda *args: (302, {}, b""))
        with self.assertRaises(SourceError):
            redirect.get(url)
        self.assertEqual(redirect.requests, 1)

    def test_reader_enforces_byte_and_total_deadline_limits(self):
        from swarm_forensics.delvetown.transport import Reader

        url = "https://api.delve.town/xrpc/town.delve.actor.getProfile?actor=" + DID
        bounded = Reader([DID], max_bytes=5,
                         network=lambda url, timeout, limit: (200, {}, b'{"ok":true}'[:limit]))
        with self.assertRaisesRegex(SourceError, "byte_limit"):
            bounded.get(url)
        self.assertEqual(bounded.body_bytes, 5)
        now = [0.0]
        deadline = Reader([DID], total_seconds=0.5, clock=lambda: now[0],
                          sleep=lambda seconds: now.__setitem__(0, now[0] + seconds),
                          network=lambda *args: (200, {}, b'{"ok":true}'))
        deadline.get(url)
        with self.assertRaisesRegex(SourceError, "deadline_limit"):
            deadline.get(url)
        self.assertEqual(deadline.requests, 1)
