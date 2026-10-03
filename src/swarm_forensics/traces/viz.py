"""Aggregate the normalized trace tables into the viewer data file.

Streams events.jsonl and edges.jsonl one line at a time and writes a compact
summary JSON: totals, per-dataset daily counts, technique families, actor
hints, top targets, zz-nonce recurrence, gem name stems, and the verbatim
edge ledger. The output feeds data/viz_mock/v4_traces/index.html.

Usage (run through make): make traces-viz-build
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

EVENTS_PATH = Path("data/raw/traces/events.jsonl")
EDGES_PATH = Path("data/raw/traces/edges.jsonl")
OUT_PATH = Path("data/viz_mock/v4_traces/data/viewer-data.json")

DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}")
ZZ_NONCE = re.compile(r"zz_nonce=([0-9A-Za-z]+)")
GEM_NAME = re.compile(r"^rubygems:(.+)$")
TRAILING_DIGITS = re.compile(r"\d+$")


def _iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def build_summary(events_path: Path, edges_path: Path) -> dict[str, Any]:
    """Aggregate both tables. Never loads a complete table into memory."""
    by_dataset: Counter = Counter()
    actions: dict[str, Counter] = {}
    hints: dict[str, Counter] = {}
    families: Counter = Counter()
    task_families: Counter = Counter()
    daily: dict[str, Counter] = {}
    bounds: dict[str, dict[str, str]] = {}
    top_targets: dict[str, Counter] = {}
    zz_nonces: Counter = Counter()
    gem_stems: Counter = Counter()

    for row in _iter_jsonl(events_path):
        dataset = row["dataset"]
        by_dataset[dataset] += 1
        actions.setdefault(dataset, Counter())[row["action"]] += 1
        hints.setdefault(dataset, Counter())[row["actor_hint"]] += 1
        families[row["technique_family"]] += 1
        task_families[row.get("task_family") or "unlabeled"] += 1

        time = row["time"]
        if time and DATE_PREFIX.match(time):
            day = time[:10]
            daily.setdefault(day, Counter())[dataset] += 1
            slot = bounds.setdefault(dataset, {"min": time, "max": time})
            slot["min"] = min(slot["min"], time)
            slot["max"] = max(slot["max"], time)

        target = row["target"]
        if target:
            top_targets.setdefault(dataset, Counter())[target] += 1

        if dataset == "arquivo":
            for nonce in ZZ_NONCE.findall(row["notes"]):
                zz_nonces[nonce] += 1
        elif dataset == "rubygems" and row["action"] == "register":
            match = GEM_NAME.match(target)
            if match:
                stem = TRAILING_DIGITS.sub("", match.group(1))
                if stem:
                    gem_stems[stem] += 1

    edges = list(_iter_jsonl(edges_path))

    return {
        "totals": {
            "events": sum(by_dataset.values()),
            "edges": len(edges),
            "by_dataset": dict(sorted(by_dataset.items())),
        },
        "actions": {d: dict(sorted(c.items())) for d, c in sorted(actions.items())},
        "hints": {d: dict(sorted(c.items())) for d, c in sorted(hints.items())},
        "families": sorted(families.items(), key=lambda kv: (-kv[1], kv[0])),
        "task_families": sorted(task_families.items(), key=lambda kv: (-kv[1], kv[0])),
        "daily": {
            day: dict(sorted(c.items())) for day, c in sorted(daily.items())
        },
        "time_bounds": {
            d: {"min": b["min"], "max": b["max"]} for d, b in sorted(bounds.items())
        },
        "top_targets": {
            d: c.most_common(12) for d, c in sorted(top_targets.items())
        },
        "zz_nonces": zz_nonces.most_common(20),
        "gem_stems": gem_stems.most_common(12),
        "edges": edges,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--events", type=Path, default=EVENTS_PATH)
    parser.add_argument("--edges", type=Path, default=EDGES_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args(argv)

    for needed in (args.events, args.edges):
        if not needed.exists():
            raise SystemExit(f"missing input: {needed} (run make traces-normalize)")

    summary = build_summary(args.events, args.edges)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=1, sort_keys=True)
        handle.write("\n")
    print(
        f"wrote {args.out}: {summary['totals']['events']} events, "
        f"{summary['totals']['edges']} edges"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
