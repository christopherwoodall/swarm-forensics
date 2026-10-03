"""Summarize the normalized trace tables.

Reads data/raw/traces/events.jsonl and edges.jsonl and prints per-dataset
counts, technique-family distributions, and every bridge-candidate edge with
its competing explanation. Run through make: traces-report.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

OUT_DIR = Path("data/raw/traces")


def main() -> int:
    events_path = OUT_DIR / "events.jsonl"
    edges_path = OUT_DIR / "edges.jsonl"
    dataset_counts: Counter = Counter()
    family_counts: Counter = Counter()
    action_counts: Counter = Counter()
    hint_counts: Counter = Counter()
    edges_by_strength: Counter = Counter()

    with open(events_path, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            dataset_counts[row["dataset"]] += 1
            family_counts[row["technique_family"]] += 1
            action_counts[(row["dataset"], row["action"])] += 1
            hint_counts[(row["dataset"], row["actor_hint"])] += 1
    print("== events by dataset ==")
    for name in sorted(dataset_counts):
        print(f"  {name}: {dataset_counts[name]}")
    print("== actions by dataset ==")
    for (dataset, action), count in sorted(action_counts.items()):
        print(f"  {dataset}/{action}: {count}")
    print("== actor hints by dataset ==")
    for (dataset, hint), count in sorted(hint_counts.items()):
        print(f"  {dataset}/{hint}: {count}")
    print("== technique families (top 15) ==")
    for family, count in family_counts.most_common(15):
        print(f"  {family}: {count}")

    print("== bridge candidate edges ==")
    with open(edges_path, encoding="utf-8") as handle:
        for line in handle:
            edge = json.loads(line)
            edges_by_strength[edge["causal_strength"]] += 1
            print(
                f"  [{edge['causal_strength']}] {edge['edge_from']} -> {edge['edge_to']} "
                f"({edge['relation']})"
            )
            print(f"      competing: {edge['competing_explanation']}")
            print(f"      raw_ref: {edge['raw_ref']}")
    print("== edges by causal strength ==")
    for strength, count in sorted(edges_by_strength.items()):
        print(f"  {strength}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
