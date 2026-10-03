"""Run the stage-4 normalization and bridge probes.

Writes data/raw/traces/events.jsonl, edges.jsonl, and unresolved.jsonl. Streams
every reservoir one record at a time. Run through make: traces-normalize.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

from swarm_forensics.traces.arquivo import arquivo_event_rows, uscan_response_rows
from swarm_forensics.traces.bridges import (
    gem_wiki_overlap_edges,
    shared_relay_edges,
    urlquery_citation_edges,
)
from swarm_forensics.traces.reservoirs import (
    gem_event_rows,
    urlquery_event_rows,
    urlquery_http_rows,
)
from swarm_forensics.traces.schema import validate_edge, validate_event
from swarm_forensics.traces.wiki import wiki_event_rows

SOURCES = Path("colette-research/sources")
WIKI_ZIP = SOURCES / "rubygems-wiki-collusion/full-wiki-logs.zip"
RECORDS_GZ = SOURCES / "rubygems-wiki-collusion/records.jsonl.gz"
LINKS_GZ = SOURCES / "rubygems-wiki-collusion/links.jsonl.gz"
USCAN_ZIP = SOURCES / "us-can-data/us-canada-government-evidence-2026-09-30.zip"
UQ_ZIP = SOURCES / "urlquery-net-data/urlquery-agent-activity-2026-09-23.zip"
OUT_DIR = Path("data/raw/traces")


def iter_all_events() -> Iterator[dict[str, str]]:
    """Stream every normalized event row from all reservoirs."""
    yield from urlquery_event_rows(UQ_ZIP)
    yield from urlquery_http_rows(USCAN_ZIP)
    yield from arquivo_event_rows(USCAN_ZIP)
    yield from uscan_response_rows(USCAN_ZIP)
    yield from gem_event_rows(RECORDS_GZ)
    yield from wiki_event_rows(WIKI_ZIP)


def iter_all_edges() -> Iterator[dict[str, str]]:
    """Stream every bridge candidate edge row."""
    yield from gem_wiki_overlap_edges(RECORDS_GZ, LINKS_GZ)
    yield from urlquery_citation_edges(WIKI_ZIP, UQ_ZIP)
    yield from shared_relay_edges(RECORDS_GZ, LINKS_GZ)


def run(out_dir: Path = OUT_DIR) -> dict[str, int]:
    """Normalize all reservoirs and write outputs. Return row counts."""
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: Counter = Counter()
    problems: list[str] = []

    with open(out_dir / "events.jsonl", "w", encoding="utf-8") as events_out:
        for row in iter_all_events():
            issues = validate_event(row)
            if issues:
                problems.extend(issues)
                continue
            events_out.write(json.dumps(row) + "\n")
            counts[row["dataset"]] += 1
    with open(out_dir / "edges.jsonl", "w", encoding="utf-8") as edges_out:
        for row in iter_all_edges():
            issues = validate_edge(row)
            if issues:
                problems.extend(issues)
                continue
            edges_out.write(json.dumps(row) + "\n")
            counts["edges"] += 1
    if problems:
        for problem in problems[:10]:
            print(f"schema problem: {problem}", file=sys.stderr)
        raise SystemExit(1)
    return dict(counts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)
    counts = run(args.out_dir)
    for name in sorted(counts):
        print(f"{name}: {counts[name]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
