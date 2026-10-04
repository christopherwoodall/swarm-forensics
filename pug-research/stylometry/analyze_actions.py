#!/usr/bin/env python3
"""Action-sequence structure: computer_use turns vs our trace records.

Lexical comparison treats behavior as text. This treats behavior as
behavior: action-type distributions and transition patterns (what follows
what). If the harness leaves a structural fingerprint, it lives here:
tool-call order, failure retry shape, stuck-loop runs.

Computer side: per session_id, agent_action -> action-name sequence.
Traces side:  traces ordered by @timestamp, event type =
  incident + ':' + mime class. Sequence of what the harness captured when.

Metrics per side: unigram distribution, bigram transition matrix,
self-loop rate P(a->a), run-length stats, transition entropy.

Usage:
    python analyze_actions.py --out actions_report.json
"""

import argparse
import gzip
import json
import math
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
COMPUTER_PATH = os.path.join(RAW, "computer_use_turns.jsonl.gz")
TRACES_PATH = os.path.expanduser("~/workspace/silent-locus/openai-agent-traces/data/traces.jsonl")


def _jlines_gz(path):
    with gzip.open(path, "rt", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def computer_action_name(d):
    """Map a turn's agent_action to a canonical action name."""
    a = d.get("agent_action")
    if a is None:
        return "none"
    if isinstance(a, dict):
        act = a.get("action") or "unknown"
        # Distinguish key presses by key text; coordinates dropped (instance noise).
        if act == "key":
            return f"key:{a.get('text') or '?'}"
        return str(act)
    return "other"


def load_computer_sequences():
    """Return list of per-session action-name sequences."""
    sessions = defaultdict(list)
    n = 0
    for d in _jlines_gz(COMPUTER_PATH):
        sessions[d.get("session_id") or "nosession"].append(
            (d.get("created_at") or "", computer_action_name(d))
        )
        n += 1
    seqs = []
    for sid, turns in sessions.items():
        turns.sort(key=lambda t: t[0])
        seqs.append([a for _, a in turns])
    return seqs, n


def mime_class(m):
    m = (m or "").lower()
    if "json" in m:
        return "json"
    if "html" in m:
        return "html"
    if "excel" in m or "spreadsheet" in m:
        return "xlsx"
    if "text/plain" in m:
        return "txt"
    return "other"


def load_trace_sequence():
    """Return the global trace event sequence ordered by timestamp."""
    events = []
    with open(TRACES_PATH, "r", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            inc = (d.get("labels") or {}).get("incident") or "unknown"
            events.append((d.get("@timestamp") or "", f"{inc}:{mime_class(d.get('mime'))}"))
    events.sort(key=lambda e: e[0])
    return [e for _, e in events]


def seq_stats(seqs):
    """seqs: list of sequences. Return structural stats."""
    uni = Counter()
    bi = Counter()
    run_lengths = []
    n_self = 0
    n_trans = 0
    for s in seqs:
        cur_run = 1
        for i, a in enumerate(s):
            uni[a] += 1
            if i == 0:
                continue
            prev = s[i - 1]
            bi[(prev, a)] += 1
            n_trans += 1
            if a == prev:
                n_self += 1
                cur_run += 1
            else:
                run_lengths.append(cur_run)
                cur_run = 1
        if s:
            run_lengths.append(cur_run)
    # Transition entropy: mean H(next | current) weighted by current frequency.
    entropy = 0.0
    total_out = Counter()
    for (a, b), c in bi.items():
        total_out[a] += c
    for a, tot in total_out.items():
        h = 0.0
        for (x, b), c in bi.items():
            if x != a:
                continue
            p = c / tot
            h -= p * math.log2(p)
        entropy += (uni[a] / sum(uni.values())) * h
    run_lengths.sort()
    return {
        "n_sequences": len(seqs),
        "n_events": sum(uni.values()),
        "n_types": len(uni),
        "top_unigrams": uni.most_common(12),
        "top_bigrams": [((a, b), c) for (a, b), c in bi.most_common(12)],
        "self_loop_rate": round(n_self / n_trans, 4) if n_trans else 0.0,
        "mean_run_length": round(sum(run_lengths) / len(run_lengths), 2) if run_lengths else 0,
        "max_run_length": max(run_lengths) if run_lengths else 0,
        "transition_entropy_bits": round(entropy, 3),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="actions_report.json")
    args = ap.parse_args()

    report = {"computer_side": None, "trace_side": None, "notes": []}
    if os.path.exists(COMPUTER_PATH):
        seqs, n = load_computer_sequences()
        report["computer_side"] = seq_stats(seqs)
        report["computer_side"]["n_sessions"] = len(seqs)
        print(f"computer: {len(seqs)} sessions, {n} turns", flush=True)
    else:
        report["notes"].append("computer_use_turns not yet downloaded; slot in on arrival.")

    trace_seq = load_trace_sequence()
    report["trace_side"] = seq_stats([trace_seq])
    print(f"traces: {len(trace_seq)} events in one global sequence", flush=True)

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
