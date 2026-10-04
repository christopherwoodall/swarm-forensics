#!/usr/bin/env python3
"""Split-half within-partition baselines for every comparison method.

For each partition, split docs into even/odd halves, build both halves as
partitions in a scratch DB, and run every method between the halves. Halves
of the same partition should beat every cross-partition pair -- that is the
within-partition ceiling against which cross-partition numbers are read.

Adversarial fix (#10): without this control, "closest pair" bolding in the
matrix invites reading noise as signal.

Usage:
    python baselines.py --db lexdb.sqlite --out baselines.json
"""

import argparse
import itertools
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexdb import PARTITIONS, SCHEMA, TOKENIZERS, build_partition  # noqa: E402
from compare import MATRIX_PRESETS, run_one, LexDB  # noqa: E402


def half_factory(factory, parity):
    def gen():
        for i, (doc_id, text) in enumerate(factory()):
            if i % 2 == parity:
                yield f"{doc_id}::h{parity}", text
    return gen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="lexdb.sqlite")
    ap.add_argument("--out", default="baselines.json")
    ap.add_argument("--tokenizers", default="word,subword,char4,funcwords")
    args = ap.parse_args()

    tokenizers = [t.strip() for t in args.tokenizers.split(",")]
    scratch = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_baselines_scratch.sqlite")
    if os.path.exists(scratch):
        os.remove(scratch)
    con = sqlite3.connect(scratch)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    names = [n for n in PARTITIONS if not PARTITIONS[n][1].startswith("DIAGNOSTIC")]
    for name in names:
        side, source, factory = PARTITIONS[name]
        for parity in (0, 1):
            hname = f"{name}__h{parity}"
            print(f"Building {hname} ...", flush=True)
            build_partition(cur, hname, side, source + " (split-half)",
                            half_factory(factory, parity), tokenizers)
            con.commit()
    con.close()

    db = LexDB(scratch)
    results = {}
    for name in names:
        a, b = f"{name}__h0", f"{name}__h1"
        results[name] = []
        for method, params in MATRIX_PRESETS:
            # Skip superseded degenerate config (two-profile delta no longer exists).
            rec = run_one(db, method, a, b, dict(params))
            rec["within_partition"] = name
            results[name].append({
                "method": method, "params": params,
                "headline": _headline(method, rec["results"]),
                "results": rec["results"],
            })
            print(f"{method:<15}{a} vs {b:<14}{_headline(method, rec['results'])}", flush=True)

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    os.remove(scratch)
    print(f"Wrote {args.out}")


def _headline(method, results):
    if "error" in results:
        return "ERROR"
    if method == "jaccard_topn":
        return f"J={results['jaccard']:.3f}"
    if method == "cosine_tfidf":
        return f"cos={results['cosine_tfidf']:.3f}"
    if method == "keyness":
        mx = 0.0
        for v in results.values():
            for _, s, _, _ in v:
                mx = max(mx, abs(s))
        return f"max|G2|={mx:.1f}"
    if method == "spearman":
        return f"rho={results['spearman_rho']}"
    if method == "shared_ngrams":
        return f"J={results['jaccard']:.3f}"
    if method == "burrows_delta":
        return f"delta={results['burrows_delta']}"
    if method == "char_cosine":
        return f"cos={results['char_cosine']:.3f}"
    return ""


if __name__ == "__main__":
    main()
