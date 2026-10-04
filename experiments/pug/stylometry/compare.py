#!/usr/bin/env python3
"""Pairwise stylometric comparison across lexdb partitions.

Methods:
- jaccard_topn: Jaccard similarity on top-N vocabularies.
- cosine_tfidf: Cosine similarity on TF-IDF vectors.
- keyness: Log-likelihood (G2) distinctive terms per side.
- spearman: Rank correlation of term frequencies on shared terms.
- shared_ngrams: Jaccard on top-N bigrams/trigrams.
- burrows_delta: Burrows Delta on top-N frequent words.
- char_cosine: Cosine similarity on character 4-gram vectors.

Every run gets logged to runs_log.jsonl with its parameters and results.
Use --matrix to run the full preset matrix across all partition pairs.

Usage:
    python compare.py --db lexdb.sqlite --matrix
    python compare.py --db lexdb.sqlite --pair wiki evals --method keyness
"""

import argparse
import datetime
import itertools
import json
import math
import os
import sqlite3
import sys
from collections import Counter

RUNS_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs_log.jsonl")


class LexDB:
    """Read-only accessor for the partitioned lexical database."""

    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.con.row_factory = sqlite3.Row

    def partitions(self):
        rows = self.con.execute("SELECT name, side, n_docs, n_tokens FROM partitions")
        return [dict(r) for r in rows]

    def top_terms(self, partition, tokenizer, n):
        rows = self.con.execute(
            "SELECT term, tf, df FROM terms WHERE partition=? AND tokenizer=?"
            " ORDER BY tf DESC LIMIT ?",
            (partition, tokenizer, n),
        )
        return [(r["term"], r["tf"], r["df"]) for r in rows]

    def term_tf(self, partition, tokenizer):
        rows = self.con.execute(
            "SELECT term, tf FROM terms WHERE partition=? AND tokenizer=?",
            (partition, tokenizer),
        )
        return {r["term"]: r["tf"] for r in rows}

    def top_ngrams(self, partition, n, topn):
        rows = self.con.execute(
            "SELECT gram, tf FROM ngrams WHERE partition=? AND n=? ORDER BY tf DESC LIMIT ?",
            (partition, n, topn),
        )
        return [(r["gram"], r["tf"]) for r in rows]

    def bg_doc_count(self, tokenizer):
        """Background document counts per term across all partitions (for IDF)."""
        rows = self.con.execute(
            "SELECT term, SUM(df) AS df FROM terms WHERE tokenizer=? GROUP BY term",
            (tokenizer,),
        )
        return {r["term"]: r["df"] for r in rows}

    def total_docs(self):
        row = self.con.execute("SELECT SUM(n_docs) AS s FROM partitions").fetchone()
        return row["s"] or 1


def jaccard_topn(db, a, b, tokenizer="word", n=1000):
    """Jaccard similarity on top-N term sets."""
    sa = {t for t, _, _ in db.top_terms(a, tokenizer, n)}
    sb = {t for t, _, _ in db.top_terms(b, tokenizer, n)}
    inter = sa & sb
    union = sa | sb
    return {
        "jaccard": len(inter) / len(union) if union else 0.0,
        "n_overlap": len(inter),
        "n_union": len(union),
        "overlap_sample": sorted(inter)[:25],
    }


def cosine_tfidf(db, a, b, tokenizer="word", n=5000):
    """Cosine similarity on TF-IDF vectors over the union of top-N terms."""
    ta = dict((t, tf) for t, tf, _ in db.top_terms(a, tokenizer, n))
    tb = dict((t, tf) for t, tf, _ in db.top_terms(b, tokenizer, n))
    vocab = set(ta) | set(tb)
    bg = db.bg_doc_count(tokenizer)
    total = db.total_docs()
    dot = na = nb = 0.0
    for t in vocab:
        idf = math.log((1 + total) / (1 + bg.get(t, 0))) + 1.0
        va = ta.get(t, 0) * idf
        vb = tb.get(t, 0) * idf
        dot += va * vb
        na += va * va
        nb += vb * vb
    cos = dot / math.sqrt(na * nb) if na and nb else 0.0
    return {"cosine_tfidf": cos, "vocab_size": len(vocab)}


def keyness(db, a, b, tokenizer="word", n=5000, top_k=20):
    """Log-likelihood G2 keyness. Reports distinctive terms for each side."""
    ta = dict((t, tf) for t, tf, _ in db.top_terms(a, tokenizer, n))
    tb = dict((t, tf) for t, tf, _ in db.top_terms(b, tokenizer, n))
    ca = sum(ta.values())
    cb = sum(tb.values())
    scored = []
    for t in set(ta) | set(tb):
        oa = ta.get(t, 0)
        ob = tb.get(t, 0)
        ea = ca * (oa + ob) / (ca + cb)
        eb = cb * (oa + ob) / (ca + cb)
        g2 = 0.0
        if oa > 0 and ea > 0:
            g2 += oa * math.log(oa / ea)
        if ob > 0 and eb > 0:
            g2 += ob * math.log(ob / eb)
        g2 *= 2
        # Sign: positive means distinctive for a, negative for b.
        exp_a = oa / ca if ca else 0
        exp_b = ob / cb if cb else 0
        sign = 1 if exp_a >= exp_b else -1
        scored.append((t, sign * g2, oa, ob))
    scored.sort(key=lambda x: -abs(x[1]))
    top_a = [(t, round(s, 1), oa, ob) for t, s, oa, ob in scored if s > 0][:top_k]
    top_b = [(t, round(s, 1), oa, ob) for t, s, oa, ob in scored if s < 0][:top_k]
    return {
        f"distinctive_{a}": top_a,
        f"distinctive_{b}": top_b,
    }


def spearman(db, a, b, tokenizer="word", n=5000):
    """Spearman rank correlation of term frequencies on shared terms."""
    ta = dict((t, tf) for t, tf, _ in db.top_terms(a, tokenizer, n))
    tb = dict((t, tf) for t, tf, _ in db.top_terms(b, tokenizer, n))
    shared = set(ta) & set(tb)
    if len(shared) < 3:
        return {"spearman_rho": None, "n_shared": len(shared)}
    ra = {t: i for i, t in enumerate(sorted(shared, key=lambda t: -ta[t]))}
    rb = {t: i for i, t in enumerate(sorted(shared, key=lambda t: -tb[t]))}
    xs = [ra[t] for t in shared]
    ys = [rb[t] for t in shared]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    rho = num / den if den else 0.0
    return {"spearman_rho": round(rho, 4), "n_shared": len(shared)}


def shared_ngrams(db, a, b, ngram_n=2, topn=2000):
    """Jaccard on top-N n-grams plus the top shared phrases."""
    ga = dict(db.top_ngrams(a, ngram_n, topn))
    gb = dict(db.top_ngrams(b, ngram_n, topn))
    sa, sb = set(ga), set(gb)
    inter = sa & sb
    union = sa | sb
    top_shared = sorted(inter, key=lambda g: -(ga[g] + gb[g]))[:20]
    return {
        "ngram_n": ngram_n,
        "jaccard": len(inter) / len(union) if union else 0.0,
        "n_overlap": len(inter),
        "top_shared": [(g, ga[g], gb[g]) for g in top_shared],
    }


def burrows_delta(db, a, b, tokenizer="word", n=200):
    """Burrows Delta on the n most frequent words.

    Z-scores come from the background of ALL partitions in the database.
    Two-profile z-scoring is degenerate (Delta is always 2.0), so it is
    not used. Lower Delta means closer style.
    """
    parts = [p["name"] for p in db.partitions()]
    tf_all = {p: db.term_tf(p, tokenizer) for p in parts}
    totals = {p: sum(tf_all[p].values()) or 1 for p in parts}
    vocab = sorted(
        set().union(*[set(t) for t in tf_all.values()]),
        key=lambda t: -sum(tf_all[p].get(t, 0) for p in parts),
    )[:n]
    # Background mean and std of relative frequencies across partitions.
    stats = {}
    for t in vocab:
        xs = [tf_all[p].get(t, 0) / totals[p] for p in parts]
        mean = sum(xs) / len(xs)
        var = sum((x - mean) ** 2 for x in xs) / len(xs)
        stats[t] = (mean, math.sqrt(var) or 1e-9)
    delta = 0.0
    for t in vocab:
        mean, std = stats[t]
        za = (tf_all[a].get(t, 0) / totals[a] - mean) / std
        zb = (tf_all[b].get(t, 0) / totals[b] - mean) / std
        delta += abs(za - zb)
    return {"burrows_delta": round(delta / n, 4), "n_words": n}


def char_cosine(db, a, b, n=5000):
    """Cosine similarity on character 4-gram TF vectors."""
    ta = dict((t, tf) for t, tf, _ in db.top_terms(a, "char4", n))
    tb = dict((t, tf) for t, tf, _ in db.top_terms(b, "char4", n))
    vocab = set(ta) | set(tb)
    dot = sum(ta.get(t, 0) * tb.get(t, 0) for t in vocab)
    na = math.sqrt(sum(v * v for v in ta.values()))
    nb = math.sqrt(sum(v * v for v in tb.values()))
    return {"char_cosine": dot / (na * nb) if na and nb else 0.0}


METHODS = {
    "jaccard_topn": jaccard_topn,
    "cosine_tfidf": cosine_tfidf,
    "keyness": keyness,
    "spearman": spearman,
    "shared_ngrams": shared_ngrams,
    "burrows_delta": burrows_delta,
    "char_cosine": char_cosine,
}

# Preset run matrix. Each entry: (method, params).
MATRIX_PRESETS = [
    ("jaccard_topn", {"tokenizer": "word", "n": 1000}),
    ("jaccard_topn", {"tokenizer": "word", "n": 5000}),
    ("cosine_tfidf", {"tokenizer": "word", "n": 5000}),
    ("cosine_tfidf", {"tokenizer": "funcwords", "n": 200}),
    ("keyness", {"tokenizer": "word", "n": 5000, "top_k": 20}),
    ("spearman", {"tokenizer": "word", "n": 5000}),
    ("shared_ngrams", {"ngram_n": 2, "topn": 2000}),
    ("shared_ngrams", {"ngram_n": 3, "topn": 2000}),
    ("burrows_delta", {"tokenizer": "word", "n": 200}),
    ("char_cosine", {"n": 5000}),
]


def run_one(db, method, a, b, params):
    """Execute one run. Return the log record."""
    fn = METHODS[method]
    result = fn(db, a, b, **params)
    return {
        "run_id": f"{method}::{a}::{b}::{abs(hash(json.dumps(params, sort_keys=True))) % 10**8:08d}",
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "method": method,
        "pair": [a, b],
        "params": params,
        "results": result,
    }


def log_run(record):
    """Append one run record to the runs log."""
    with open(RUNS_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")


def headline(method, results):
    """Extract one headline number per method for the summary table."""
    if method == "jaccard_topn":
        return f"J={results['jaccard']:.3f} (n={results['n_overlap']})"
    if method == "cosine_tfidf":
        return f"cos={results['cosine_tfidf']:.3f}"
    if method == "keyness":
        return "keyness top-20 each side"
    if method == "spearman":
        return f"rho={results['spearman_rho']}"
    if method == "shared_ngrams":
        return f"J={results['jaccard']:.3f} (n={results['n_overlap']})"
    if method == "burrows_delta":
        return f"delta={results['burrows_delta']}"
    if method == "char_cosine":
        return f"cos={results['char_cosine']:.3f}"
    return ""


def main():
    ap = argparse.ArgumentParser(description="Pairwise stylometric comparison.")
    ap.add_argument("--db", default="lexdb.sqlite")
    ap.add_argument("--pair", help="Two partitions, e.g. 'wiki evals'.")
    ap.add_argument("--method", default="jaccard_topn", choices=list(METHODS))
    ap.add_argument("--tokenizer", default="word")
    ap.add_argument("--topn", type=int, default=1000)
    ap.add_argument("--matrix", action="store_true",
                    help="Run the full preset matrix across all pairs.")
    args = ap.parse_args()

    db = LexDB(args.db)
    parts = [p["name"] for p in db.partitions()]
    if len(parts) < 2:
        sys.exit("Need at least two partitions. Run build_lexdb.py first.")

    runs = []
    if args.matrix:
        for a, b in itertools.combinations(sorted(parts), 2):
            for method, params in MATRIX_PRESETS:
                runs.append((method, a, b, params))
    else:
        if not args.pair:
            sys.exit("Pass --pair 'a b' or --matrix.")
        a, b = args.pair.split()
        params = {"tokenizer": args.tokenizer, "n": args.topn}
        if args.method == "shared_ngrams":
            params = {"ngram_n": 2, "topn": args.topn}
        if args.method == "char_cosine":
            params = {"n": args.topn}
        runs.append((args.method, a, b, params))

    print(f"{'method':<15}{'pair':<22}{'headline'}")
    for method, a, b, params in runs:
        try:
            record = run_one(db, method, a, b, params)
        except Exception as e:  # noqa: BLE001 - log the failure, keep the matrix running
            record = {
                "run_id": f"{method}::{a}::{b}::failed",
                "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "method": method, "pair": [a, b], "params": params,
                "results": {"error": str(e)},
            }
        log_run(record)
        hl = headline(method, record["results"]) if "error" not in record["results"] else "ERROR"
        print(f"{method:<15}{a+' vs '+b:<22}{hl}", flush=True)
    print(f"\nLogged {len(runs)} runs to {RUNS_LOG}")


if __name__ == "__main__":
    main()
