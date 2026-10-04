"""Export structural references and audit private record provenance."""

import hashlib
import json
import sqlite3
import stat
from collections import Counter
from itertools import zip_longest
from pathlib import Path

from .collector import canonical, private_file
from .records import SourceError, normalize, timestamp
from .transport import Reader


def iter_edges(conn):
    """Label explicit references as structural associations, never causal use."""
    for uri, encoded, source_request in conn.execute(
            "SELECT uri, normalized, source_request FROM posts ORDER BY uri"):
        row = json.loads(encoded)
        targets = [("reply_to", row.get("reply_parent")), ("thread_root", row.get("reply_root"))]
        targets.extend(("quote", target) for target in row.get("quote_uris", []))
        targets.extend(("mention", target) for target in row.get("mentions", []))
        for relation, target in targets:
            if not target:
                continue
            table, key = ("actors", "did") if relation == "mention" else ("posts", "uri")
            present = conn.execute(f"SELECT 1 FROM {table} WHERE {key}=?", (target,)).fetchone()
            identity = canonical([uri, relation, target]).encode()
            yield {"edge_id": hashlib.sha256(identity).hexdigest(),
                   "edge_from": uri, "edge_to": target, "relation": relation,
                   "evidence_type": "explicit_record_reference",
                   "causal_strength": "temporal_structural_association_only",
                   "competing_explanation": "A reference does not prove retrieval or causal use.",
                   "raw_ref": f"archive.sqlite:posts:{uri}", "notes": "Public source record only.",
                   "source_request": source_request, "target_in_archive": bool(present)}


def read_connection(dest):
    """Open one existing source archive without permitting database writes."""
    return sqlite3.connect((Path(dest) / "archive.sqlite").resolve().as_uri() + "?mode=ro", uri=True)


def record_view(dest, uri):
    """Read one complete retained post without truncation or network requests."""
    with read_connection(dest) as conn:
        found = conn.execute("SELECT normalized, source_request FROM posts WHERE uri=?",
                             (uri,)).fetchone()
        if found is None:
            raise SourceError("record is absent from the private snapshot")
        post = json.loads(found[0])
        actor = json.loads(conn.execute("SELECT snapshot FROM actors WHERE did=?",
                                       (post["actor_did"],)).fetchone()[0])
        request = json.loads(conn.execute("SELECT metadata FROM requests WHERE id=?",
                                         (found[1],)).fetchone()[0])
        return {"post": post, "source_handle": actor["handle"], "source_request": request}


def audit(dest):
    """Verify exact projections, bounds, references, and private permissions."""
    dest = Path(dest)
    if dest.is_symlink() or stat.S_IMODE(dest.stat().st_mode) != 0o700:
        raise SourceError("unsafe archive directory permissions")
    for path in dest.iterdir():
        if path.is_symlink() or not path.is_file() or stat.S_IMODE(path.stat().st_mode) != 0o600:
            raise SourceError("unsafe archive file or permissions")
    with read_connection(dest) as conn:
        if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise SourceError("source archive integrity failure")
        scope = json.loads(conn.execute("SELECT value FROM metadata WHERE key='scope'").fetchone()[0])
        cohort = {row[0] for row in conn.execute("SELECT did FROM actors")}
        route_check = Reader(cohort)
        byte_count = 0
        request_count = 0
        for (encoded,) in conn.execute("SELECT metadata FROM requests"):
            request = json.loads(encoded)
            route_check.validate_url(request["url"])
            if request.get("method") != "GET":
                raise SourceError("non-GET source request")
            byte_count += request["body_bytes"]
            request_count += 1
        if (request_count != scope["requests"] or byte_count != scope["body_bytes"]
                or request_count > 500 or byte_count > 100_000_000):
            raise SourceError("request provenance or network budget mismatch")
        start, end = timestamp(scope["window_start"]), timestamp(scope["window_end"])
        count = 0
        oldest = latest = None
        replies = 0
        authors = Counter()
        with (dest / "posts.jsonl").open() as exported:
            originals = conn.execute("SELECT raw, normalized, source_request FROM posts ORDER BY uri")
            for original, line in zip_longest(originals, exported):
                if original is None or line is None:
                    raise SourceError("post export count mismatch")
                raw, normalized, request_id = original
                row = json.loads(normalized)
                expected = normalize(json.loads(raw), row["actor_did"], end)
                request = json.loads(conn.execute("SELECT metadata FROM requests WHERE id=?",
                                                  (request_id,)).fetchone()[0])
                expected.update(source_request=request_id, collected_at=request["received_at"])
                if (expected != row or json.loads(line) != row or row["actor_did"] not in cohort
                        or request["status"] != 200):
                    raise SourceError("post provenance or export mismatch")
                when = timestamp(row["created_at"])
                if not start <= when <= end:
                    raise SourceError("post outside approved time window")
                oldest = min(oldest, when) if oldest else when
                latest = max(latest, when) if latest else when
                authors[row["actor_did"]] += 1
                replies += bool(row.get("reply_parent"))
                count += 1
        if count > 10_000:
            raise SourceError("post budget exceeded")
        edge_count = missing = 0
        kinds = Counter()
        with (dest / "edges.jsonl").open() as exported:
            for expected, line in zip_longest(iter_edges(conn), exported):
                if expected is None or line is None or json.loads(line) != expected:
                    raise SourceError("structural edge export mismatch")
                edge_count += 1
                kinds[expected["relation"]] += 1
                missing += (not expected["target_in_archive"] and expected["relation"] != "mention")
        coverage = json.loads((dest / "coverage.json").read_text())
        complete = conn.execute("SELECT COUNT(*) FROM actors WHERE coverage='complete'").fetchone()[0]
        if coverage["posts"] != count or coverage["accounts_complete"] != complete:
            raise SourceError("coverage receipt mismatch")
        size = sum(path.stat().st_size for path in dest.iterdir())
        if size > 100_000_000:
            raise SourceError("archive byte budget exceeded")
        return {"verified": True, "posts": count, "posting_accounts": len(authors),
                "cohort_accounts": len(cohort), "accounts_complete": complete,
                "reply_posts": replies, "edges": edge_count, "edge_types": dict(kinds),
                "unresolved_post_references": missing,
                "oldest_post": oldest.isoformat() if oldest else None,
                "latest_post": latest.isoformat() if latest else None,
                "requests": request_count, "downloaded_bytes": byte_count, "archive_bytes": size,
                "window_start": scope["window_start"], "window_end": scope["window_end"],
                "stop_reason": scope["stop_reason"]}


def export_report(dest):
    """Write a private structural edge file and content-free coverage report."""
    dest = Path(dest)
    with read_connection(dest) as conn, private_file(dest / "edges.jsonl") as output:
        for edge in iter_edges(conn):
            output.write(canonical(edge) + "\n")
    receipt = audit(dest)
    with read_connection(dest) as conn, private_file(dest / "REPORT.md") as output:
        output.write("# Private Delvetown pilot\n\nPublication remains deferred.\n\n")
        output.write("## Verified census\n\n")
        for key, value in receipt.items():
            output.write(f"- {key}: {canonical(value)}\n")
        output.write("\n## Account coverage\n\n")
        for snapshot, coverage, pages, seen, did in conn.execute(
                "SELECT snapshot, coverage, pages, seen, did FROM actors ORDER BY did"):
            profile = json.loads(snapshot)
            posts = conn.execute("SELECT COUNT(*) FROM posts WHERE did=?", (did,)).fetchone()[0]
            output.write(f"- {profile['handle']}: {posts} retained; {seen} inspected; "
                         f"{pages} pages; {coverage}.\n")
        output.write("\n## Evidence limits\n\n")
        output.write("This is a current-public-record snapshot, not a historical event log.\n")
        output.write("Missing references may be outside the cohort, outside the window, or unavailable.\n")
        output.write("Account labels are self-reported. References do not prove causal consumption.\n")
        output.write("Response hashes support request provenance; exact response bodies are not retained.\n")
        output.write("Record CIDs are preserved, not cryptographically reverified.\n")
        output.write("Archive bytes above exclude this report's own size.\n")


def inspect(dest, *, limit=8, excerpt_chars=600):
    """Return bounded private discussion samples without making network requests."""
    if not 1 <= limit <= 20 or not 1 <= excerpt_chars <= 2000:
        raise SourceError("invalid inspection limits")
    result = {"summary": audit(dest), "active_accounts": [], "threads": []}
    result["summary"]["reply_percent"] = round(
        100 * result["summary"]["reply_posts"] / max(1, result["summary"]["posts"]), 2)
    with read_connection(dest) as conn:
        for did, count in conn.execute(
                "SELECT did, COUNT(*) AS n FROM posts GROUP BY did ORDER BY n DESC, did LIMIT ?",
                (limit,)):
            profile = json.loads(conn.execute("SELECT snapshot FROM actors WHERE did=?",
                                              (did,)).fetchone()[0])
            result["active_accounts"].append({"did": did, "handle": profile["handle"],
                                               "posts": count})
        threads = conn.execute("""
            SELECT COALESCE(json_extract(normalized, '$.reply_root'), uri) AS root,
                   COUNT(*) AS n, COUNT(DISTINCT did)
            FROM posts GROUP BY root ORDER BY n DESC, root LIMIT ?
        """, (limit,)).fetchall()
        for root, count, actors in threads:
            root_record = conn.execute("SELECT normalized FROM posts WHERE uri=?", (root,)).fetchone()
            sample = root_record or conn.execute("""
                SELECT normalized FROM posts WHERE json_extract(normalized, '$.reply_root')=?
                ORDER BY uri LIMIT 1
            """, (root,)).fetchone()
            row = json.loads(sample[0])
            handle = json.loads(conn.execute("SELECT snapshot FROM actors WHERE did=?",
                                             (row["actor_did"],)).fetchone()[0])["handle"]
            result["threads"].append({"root_uri": root, "posts": count, "posting_accounts": actors,
                                      "root_in_archive": bool(root_record), "sample_uri": row["uri"],
                                      "sample_handle": handle, "excerpt": row["text"][:excerpt_chars]})
        missing = {edge["edge_to"] for edge in iter_edges(conn)
                   if not edge["target_in_archive"] and edge["relation"] != "mention"}
        result["summary"]["unresolved_reference_targets"] = len(missing)
    return result
