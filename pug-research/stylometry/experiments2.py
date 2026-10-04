#!/usr/bin/env python3
"""Non-lexical style experiments on functionally-matched partitions.

Bag-of-words misses these by construction. Each experiment is stdlib-only,
streams documents (capped per partition), and logs a one-line result to
runs_log.jsonl with method="style_exp".

Experiments:
  punct      punctuation profiles per 1k tokens, cosine between partitions
  caps_digit capitalization ratio + digit density
  sentlen    sentence-length distribution: mean, p90, distance
  markdown   markdown-structure markers per doc
  urls       URL density + embedding style (bare/linked/relay-wrapped)
  hedge      hedging vs assertive ratio
  ttr        type-token ratio on fixed 10k-token samples

Usage:
    python experiments2.py --db lexdb_v2.sqlite --pairs ours_wiki:vil_chat_agent,...
"""

import argparse
import datetime
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexdb import tok_word  # noqa: E402
from build_lexdb_v2 import PARTITIONS_V2  # noqa: E402
from compare import RUNS_LOG  # noqa: E402

PUNCT = sorted(set("!?") | set(":;-") | set("()[]{}"))

HEDGE = frozenset("maybe might could likely seems perhaps possibly probably appears appear suggests suggest seem".split())
ASSERT = frozenset("must will always never certainly definitely ensure guarantee required shall".split())
RELAY_PAT = re.compile(r"jina|allorigins|cors|proxy|archive\.org|arquivo|webcache|12ft", re.I)
URL_RE = re.compile(r"https?://[^\s)>\]]+")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(https?://[^)]+\)")
SENT_RE = re.compile(r"[^.!?]+[.!?]+")

MAX_DOCS = 20000  # deterministic cap per partition (doc order)


def stream_docs(name, cap=MAX_DOCS):
    _, _, factory = PARTITIONS_V2[name]
    n = 0
    for _, text in factory():
        yield text
        n += 1
        if n >= cap:
            break


def exp_punct(name):
    pc = Counter()
    ntok = 0
    for text in stream_docs(name):
        toks = tok_word(text)
        ntok += len(toks)
        for ch in text:
            if ch in PUNCT:
                pc[ch] += 1
    k = 1000.0 / (ntok or 1)
    return {"per1k": {c: round(pc[c] * k, 3) for c in PUNCT}, "n_tokens": ntok}


def punct_cosine(a, b):
    va = a["per1k"]
    vb = b["per1k"]
    dot = sum(va[c] * vb[c] for c in PUNCT)
    na = math.sqrt(sum(v * v for v in va.values()))
    nb = math.sqrt(sum(v * v for v in vb.values()))
    return round(dot / (na * nb), 4) if na and nb else 0.0


def exp_caps_digit(name):
    up = alpha = digit = 0
    for text in stream_docs(name):
        for ch in text:
            if ch.isalpha():
                alpha += 1
                if ch.isupper():
                    up += 1
            elif ch.isdigit():
                digit += 1
    tot = alpha + digit or 1
    return {"caps_ratio": round(up / (alpha or 1), 4),
            "digit_per1k": round(digit / tot * 1000, 2)}


def exp_sentlen(name):
    lens = []
    for text in stream_docs(name):
        for m in SENT_RE.finditer(text):
            w = len(tok_word(m.group(0)))
            if w:
                lens.append(w)
        if len(lens) > 60000:
            break
    lens.sort()
    if not lens:
        return {"mean": 0, "p90": 0, "n": 0}
    mean = sum(lens) / len(lens)
    p90 = lens[int(0.9 * len(lens))]
    return {"mean": round(mean, 2), "p90": p90, "n": len(lens),
            "hist": Counter(min(l // 5, 12) for l in lens)}


def sentlen_dist(a, b):
    # L1 distance between binned histograms (normalized).
    ha, hb = a["hist"], b["hist"]
    keys = set(ha) | set(hb)
    sa = sum(ha.values()) or 1
    sb = sum(hb.values()) or 1
    return round(sum(abs(ha[k] / sa - hb[k] / sb) for k in keys) / 2, 4)


def exp_markdown(name):
    n = 0
    marks = Counter()
    for text in stream_docs(name):
        n += 1
        lines = text.split("\n")
        if any(re.match(r"#{1,6}\s", l) for l in lines):
            marks["header"] += 1
        if any(re.match(r"\s*[-*]\s", l) for l in lines):
            marks["bullet"] += 1
        if any(re.match(r"\s*\d+[.)]\s", l) for l in lines):
            marks["numlist"] += 1
        if "```" in text:
            marks["fence"] += 1
        if any(l.count("|") >= 2 for l in lines):
            marks["table"] += 1
    return {"docs": n, "frac": {k: round(marks[k] / (n or 1), 4) for k in
                               ("header", "bullet", "numlist", "fence", "table")}}


def markdown_dist(a, b):
    fa, fb = a["frac"], b["frac"]
    return round(math.sqrt(sum((fa[k] - fb[k]) ** 2 for k in fa)), 4)


def exp_urls(name):
    ntok = 0
    n_bare = n_linked = n_relay = 0
    for text in stream_docs(name):
        ntok += len(tok_word(text))
        linked = set(m.start() for m in MD_LINK_RE.finditer(text))
        for m in URL_RE.finditer(text):
            url = m.group(0)
            if any(abs(m.start() - s) < len(url) + 20 for s in linked):
                n_linked += 1
            else:
                n_bare += 1
            if RELAY_PAT.search(url):
                n_relay += 1
    k = 1000.0 / (ntok or 1)
    return {"bare_per1k": round(n_bare * k, 3), "linked_per1k": round(n_linked * k, 3),
            "relay_frac": round(n_relay / ((n_bare + n_linked) or 1), 4)}


def exp_hedge(name):
    h = a = 0
    for text in stream_docs(name):
        for t in tok_word(text):
            if t in HEDGE:
                h += 1
            elif t in ASSERT:
                a += 1
    return {"hedge": h, "assert": a,
            "hedge_per1k_assert": round(h / ((a) or 1), 3),
            "ratio_h_over_a": round(h / (a or 1), 3)}


def exp_ttr(name, sample_tokens=10000):
    seen = set()
    tot = 0
    for text in stream_docs(name):
        for t in tok_word(text):
            seen.add(t)
            tot += 1
            if tot >= sample_tokens:
                break
        if tot >= sample_tokens:
            break
    return {"ttr": round(len(seen) / (tot or 1), 4), "tokens": tot}


EXPS = {
    "punct": (exp_punct, punct_cosine, "cosine (higher=closer)"),
    "caps_digit": (exp_caps_digit, None, "raw profiles"),
    "sentlen": (exp_sentlen, sentlen_dist, "L1 histogram distance (lower=closer)"),
    "markdown": (exp_markdown, markdown_dist, "euclidean on marker fracs (lower=closer)"),
    "urls": (exp_urls, None, "raw profiles"),
    "hedge": (exp_hedge, None, "raw counts"),
    "ttr": (exp_ttr, None, "raw TTR"),
}


def log_exp(exp, pair, result, note=""):
    rec = {"run_id": f"style_exp::{exp}::{pair[0]}::{pair[1]}",
           "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "method": "style_exp", "exp": exp, "pair": list(pair),
           "results": result, "note": note}
    with open(RUNS_LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="lexdb_v2.sqlite")
    ap.add_argument("--pairs", default=",".join(
        f"{a}:{b}" for a, b in
        [("ours_wiki", "vil_chat_agent"), ("ours_evals", "vil_goals"),
         ("ours_gems_names", "vil_code"), ("ours_traces", "vil_computer_lex"),
         ("ours_wiki", "vil_chat_all")]))
    ap.add_argument("--exps", default=",".join(EXPS))
    args = ap.parse_args()

    pairs = [tuple(p.split(":")) for p in args.pairs.split(",")]
    exps = [e.strip() for e in args.exps.split(",")]
    names = sorted({n for p in pairs for n in p})

    profiles = {}
    for exp in exps:
        fn, _, _ = EXPS[exp]
        profiles[exp] = {}
        for name in names:
            if name not in PARTITIONS_V2:
                print(f"SKIP {exp} {name}: no such partition")
                continue
            print(f"{exp}: profiling {name} ...", flush=True)
            profiles[exp][name] = fn(name)

    print(f"\n{'exp':<10}{'pair':<34}{'result'}")
    for exp in exps:
        _, distfn, direction = EXPS[exp]
        for a, b in pairs:
            if a not in profiles[exp] or b not in profiles[exp]:
                continue
            pa, pb = profiles[exp][a], profiles[exp][b]
            if distfn:
                res = {"distance": distfn(pa, pb), "direction": direction,
                       a: pa, b: pb}
                line = f"{distfn(pa, pb)} ({direction.split('(')[0].strip()})"
            else:
                res = {a: pa, b: pb}
                line = json.dumps({k: v for k, v in pa.items() if k != "hist"})[:80] + \
                       "  VS  " + json.dumps({k: v for k, v in pb.items() if k != "hist"})[:80]
            log_exp(exp, (a, b), res)
            # one-line result per experiment-pair
            print(f"{exp:<10}{a+' vs '+b:<34}{line}", flush=True)
    print(f"\nLogged style experiments to {RUNS_LOG}")


if __name__ == "__main__":
    main()
