#!/usr/bin/env python3
"""Count textual SEC county URL references in the released ProWiki revision export.

Read-only: stream the ZIP member; emit aggregate counts and redacted source IDs.
No network requests or raw URLs are written. Input ZIP is an existing local source.
"""
from __future__ import annotations

import collections
import hashlib
import html
import json
import re
import sys
import urllib.parse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
SOURCE = ROOT / "colette-research/sources/rubygems-wiki-collusion/full-wiki-logs.zip"
OUT = Path(__file__).resolve().parent / "counts.json"
# Match the published extractor. Its pipe/brace exclusion truncates some jq filters.
URL_RE = re.compile(r"https?://[^\s<>\]\"'`|{}\\]+", re.I)
COUNTY_RE = re.compile(r"county\.json", re.I)
TRAILING = ".,;:!?'\")"
HOSTS = ("jqp.vercel.app", "platform.lemino.ai", "allorigins.hexlet.app", "api.cors.lol")


def clean_url(value: str) -> str:
    value = html.unescape(value)
    while value and value[-1] in TRAILING:
        value = value[:-1]
    return value


def expanded(value: str) -> str:
    for _ in range(3):
        new = urllib.parse.unquote(value)
        if new == value:
            break
        value = new
    return value


def normalize(value: str) -> str:
    """Conservative lexical normalization, without collapsing relays or cache busters."""
    value = clean_url(value)
    parsed = urllib.parse.urlsplit(value)
    host = (parsed.hostname or "").lower()
    netloc = host + (f":{parsed.port}" if parsed.port and parsed.port not in (80, 443) else "")
    # Do not decode reserved URL characters or reorder parameters.
    value = urllib.parse.urlunsplit((parsed.scheme.lower(), netloc, parsed.path, parsed.query, ""))
    return re.sub(r"%[0-9a-fA-F]{2}", lambda m: m.group().upper(), value)


def labels_for(url: str) -> tuple[str, ...]:
    """Outer host is exclusive; embedded names MAY appear in a nested URL."""
    return tuple(h for h in HOSTS if h in expanded(url).lower())


def tally() -> dict:
    counts = collections.Counter()
    outer = collections.Counter()
    embedded = collections.Counter()
    per_day = collections.Counter()
    per_date_host = collections.Counter()
    body_host = collections.Counter()
    revtime: dict[str, set[tuple[str, str]]] = collections.defaultdict(set)
    wrapper_pairs = collections.Counter()
    unique_urls: dict[str, set[str]] = collections.defaultdict(set)
    tuples: dict[str, set[tuple[str, str, str]]] = collections.defaultdict(set)
    first_last: dict[str, list[dict]] = {}
    examples: dict[str, dict] = {}
    # ZIP source is streamed one JSONL line at a time. Do not materialize bodies.
    with zipfile.ZipFile(SOURCE) as zf, zf.open("revisions.jsonl") as member:
        for line in member:
            revision = json.loads(line)
            counts["revisions_scanned"] += 1
            body = revision.get("body") or ""
            counts["plain_county_tokens_in_all_bodies"] += len(COUNTY_RE.findall(body))
            eligible = bool(re.search(r"regCF|us-ma-|county\.json", body, re.I))
            if eligible:
                counts["eligible_revisions"] += 1
            found = []
            for match in URL_RE.finditer(body):
                raw = clean_url(match.group())
                if not raw or not COUNTY_RE.search(expanded(raw)):
                    continue
                try:
                    normal = normalize(raw)
                    host = urllib.parse.urlsplit(normal).hostname or ""
                except ValueError:
                    counts["invalid_url_candidates"] += 1
                    continue
                if not host:
                    counts["invalid_url_candidates"] += 1
                    continue
                found.append((normal, host, labels_for(raw)))
                if COUNTY_RE.search(raw):
                    counts["literal_county_url_occurrences"] += 1
                else:
                    counts["percent_only_county_url_occurrences"] += 1
            if not found:
                continue
            counts["revisions_with_county_url"] += 1
            day = str(revision.get("time", ""))[:10]
            per_day[day] += len(found)
            rev_id = str(revision["rev_id"])
            stamp = str(revision.get("time"))
            present = set()
            for normal, host, nested in found:
                counts["raw_url_occurrences"] += 1
                outer[host] += 1
                unique_urls["ALL"].add(normal)
                tuples["ALL"].add((rev_id, stamp, normal))
                revtime["ALL"].add((rev_id, stamp))
                body_host[(rev_id, host)] += 1
                per_date_host[(day, host)] += 1
                # Exactly one category for each outermost URL; nested counts overlap.
                if host in HOSTS:
                    unique_urls[host].add(normal)
                    tuples[host].add((rev_id, stamp, normal))
                    revtime[host].add((rev_id, stamp))
                for nested_host in nested:
                    embedded[nested_host] += 1
                for nested_host in nested:
                    if nested_host != host:
                        wrapper_pairs[(host, nested_host)] += 1
                if host not in first_last:
                    first_last[host] = [{"time_utc": stamp, "rev_id": rev_id}, {"time_utc": stamp, "rev_id": rev_id}]
                else:
                    if stamp < first_last[host][0]["time_utc"]:
                        first_last[host][0] = {"time_utc": stamp, "rev_id": rev_id}
                    if stamp > first_last[host][1]["time_utc"]:
                        first_last[host][1] = {"time_utc": stamp, "rev_id": rev_id}
                if host in HOSTS and host not in examples:
                    examples[host] = {"rev_id": rev_id, "time_utc": stamp,
                                      "url_sha256": hashlib.sha256(normal.encode()).hexdigest(),
                                      "outer_host": host, "embedded_host_flags": nested}
                present.add(host)
            for host in present:
                counts[f"revision_count_outer_{host}"] += 1
            # Extract newly introduced lines. A replace hunk is an upper bound.
            lines = body.split("\n")
            fresh_lines = []
            for hunk in revision.get("hunks") or []:
                if hunk.get("op") in ("insert", "replace"):
                    fresh_lines.extend(lines[hunk["b0"]:hunk["b1"]])
            fresh_body = "\n".join(fresh_lines)
            for match in URL_RE.finditer(fresh_body):
                if COUNTY_RE.search(expanded(match.group())):
                    counts["hunk_insert_or_replace_county_urls"] += 1
                    h = urllib.parse.urlsplit(clean_url(match.group())).hostname
                    if h in HOSTS:
                        counts[f"hunk_{h}"] += 1
            if revision.get("diff_base_reason") == "earlier_revisions_not_published":
                counts["county_revisions_missing_base"] += 1
    for host in HOSTS:
        unique_urls[host]  # include zero rows
        tuples[host]
    # Each source/time tuple holds one normalized URL. Repeated URLs in one revision collapse.
    result = {"source_zip": str(SOURCE.relative_to(ROOT)),
              "source_zip_sha256": hashlib.file_digest(SOURCE.open("rb"), "sha256").hexdigest(),
              "source_member": "revisions.jsonl",
              "reference_rule": "One URL-like token in a revision body containing county.json after <=3 percent decodes; nested URLs count once at the outer host.",
              "normalization_rule": "HTML entity decode, trim terminal punctuation, lowercase scheme and host, strip fragment/default port, uppercase percent triplets; preserve query order and cache-busting parameters.",
              "counts": dict(sorted(counts.items())),
              "outer_host_counts": dict(outer.most_common()),
              "embedded_host_counts_overlap": dict(embedded.most_common()),
              "unique_normalized_url_counts": {k: len(v) for k, v in unique_urls.items()},
              "unique_revision_time_url_tuple_counts": {k: len(v) for k, v in tuples.items()},
              "unique_source_object_time_counts": {k: len(v) for k, v in revtime.items()},
              "outer_inner_host_pairs": {f"{a} -> {b}": n for (a, b), n in wrapper_pairs.most_common()},
              "daily_url_occurrences": dict(sorted(per_day.items())),
              "selected_outer_host_daily_counts": {h: dict(sorted((day, n) for (day, name), n in per_date_host.items() if name == h)) for h in HOSTS},
              "outer_host_first_last": {k: v for k, v in first_last.items() if k in HOSTS},
              "redacted_examples": examples,
              "max_repeats_in_one_revision_host": {h: max((n for (rev, name), n in body_host.items() if name == h), default=0) for h in HOSTS}}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"source_zip_sha256": result["source_zip_sha256"],
                      "headline_counts": {k: counts[k] for k in ("revisions_scanned", "plain_county_tokens_in_all_bodies", "literal_county_url_occurrences", "percent_only_county_url_occurrences", "raw_url_occurrences", "hunk_insert_or_replace_county_urls")},
                      "selected_outer_hosts": {h: outer[h] for h in HOSTS},
                      "unique_normalized_url_counts": result["unique_normalized_url_counts"],
                      "unique_source_object_time_counts": result["unique_source_object_time_counts"]}, indent=2))
    print("output", OUT)
    return result


if __name__ == "__main__":
    tally()
