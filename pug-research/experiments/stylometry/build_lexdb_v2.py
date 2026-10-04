#!/usr/bin/env python3
"""Build v2 partitioned lexical database: functionally-matched partitions.

v1 (lexdb.sqlite) stays intact. This writes lexdb_v2.sqlite.

Functional pairing (apples to apples):
  ours_wiki    <-> vil_chat_agent   agent-to-agent coordination prose
  ours_evals   <-> vil_goals        task/goal statements
  ours_gems    <-> vil_code         code (+ text found in source)
  ours_traces  <-> vil_computer_lex behavioral/action traces (lexical side)
  ours_wiki    <-> vil_chat_all     contamination check (user rows included)
  (reference)    vil_memories       long-horizon agent voice, village-only

Usage:
    python build_lexdb_v2.py --db lexdb_v2.sqlite
"""

import argparse
import gzip
import json
import os
import re
import sqlite3
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_lexdb import (  # noqa: E402
    TOKENIZERS,
    SCHEMA,
    EXCLUDE_GEM_DIRS,
    iter_gems_names,
    iter_traces,
    iter_traces_clean,
    iter_wiki,
    iter_evals,
    tok_word,
    word_ngrams,
)

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
CHAT_PATH = os.path.join(RAW, "chat_messages.jsonl.gz")
GOALS_PATH = os.path.join(RAW, "agent_goals.jsonl.gz")
CODE_PATH = os.path.join(RAW, "claude_code_messages.jsonl.gz")
COMPUTER_PATH = os.path.join(RAW, "computer_use_turns.jsonl.gz")
MEMORIES_PATH = os.path.join(RAW, "agent_memories.jsonl.gz")


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


def _strided(docs, stride):
    """Deterministic 1-in-stride systematic sample (documented sampling)."""
    for i, item in enumerate(docs):
        if i % stride == 0:
            yield item


# Sampling strides for the large village partitions. The v1 traces partition
# already samples 1-in-20; the same principle applies here: systematic,
# deterministic, documented. Full builds are infeasible on the shared box
# (2 CPUs, load >10 from sibling lanes); profiles are unbiased estimates.
STRIDES = {
    "vil_chat_agent": 5,
    "vil_chat_all": 5,
    "vil_code": 5,
    "vil_computer_lex": 20,
    "vil_memories": 10,
}


def iter_vil_chat_agent():
    """Village chat, speaker_type='agent' only. ~10k user rows excluded."""
    docs = (d for d in _jlines_gz(CHAT_PATH) if d.get("speaker_type") == "agent")
    for d in _strided(docs, STRIDES["vil_chat_agent"]):
        yield d.get("id"), d.get("content") or ""
        yield d.get("id"), d.get("content") or ""


def iter_vil_chat_all():
    """Village chat, all speakers. Contamination check partition."""
    for d in _strided(_jlines_gz(CHAT_PATH), STRIDES["vil_chat_all"]):
        yield d.get("id"), d.get("content") or ""
        yield d.get("id"), d.get("content") or ""


def iter_vil_goals():
    """Village agent goals: name + short_name + description."""
    for d in _jlines_gz(GOALS_PATH):
        parts = [d.get("name") or "", d.get("short_name") or "", d.get("description") or ""]
        yield d.get("id"), "\n".join(parts)


def _extract_text(obj, out):
    """Recursively pull every 'text' string out of nested message structures."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "text" and isinstance(v, str):
                out.append(v)
            else:
                _extract_text(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _extract_text(v, out)


def iter_vil_code():
    """Claude Code assistant messages: nested content -> flat text.

    Assistant messages are agent output. User/system/result excluded.
    """
    docs = (d for d in _jlines_gz(CODE_PATH) if d.get("message_type") == "assistant")
    for d in _strided(docs, STRIDES["vil_code"]):
        out = []
        _extract_text(d.get("content"), out)
        yield d.get("id"), "\n".join(out)
        out = []
        _extract_text(d.get("content"), out)
        yield d.get("id"), "\n".join(out)


def _as_text(v):
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return "\n".join(_as_text(x) for x in v)
    if isinstance(v, dict):
        out = []
        _extract_text(v, out)
        return "\n".join(out)
    return ""


def iter_vil_computer_lex():
    """Computer-use turns, lexical side: agent_messages + output + error."""
    for d in _strided(_jlines_gz(COMPUTER_PATH), STRIDES["vil_computer_lex"]):
        parts = [
            _as_text(d.get("agent_messages")),
            _as_text(d.get("output")),
        parts = [
            _as_text(d.get("agent_messages")),
            _as_text(d.get("output")),
            _as_text(d.get("error")),
        ]
        yield d.get("id"), "\n".join(parts)


def iter_vil_memories():
    """Consolidated agent memories. Village-only reference partition."""
    for d in _strided(_jlines_gz(MEMORIES_PATH), STRIDES["vil_memories"]):
        yield d.get("id"), d.get("content") or ""
        yield d.get("id"), d.get("content") or ""


PARTITIONS_V2 = {
    # Our side (fixed iterators from build_lexdb).
    "ours_wiki": ("openai", "collusion-wiki revisions (coordination prose)", iter_wiki),
    "ours_evals": ("openai", "DeepSearchQA questions (task statements)", iter_evals),
    "ours_gems_names": ("openai", "gem dirnames only (agent-chosen names, oai-1.3.0 excluded)", iter_gems_names),
    "ours_traces": ("openai", "traces.jsonl 1-in-20 (incl. analyst notes)", iter_traces),
    "ours_traces_clean": ("openai", "traces.jsonl 1-in-20, URL+params only", iter_traces_clean),
    # Village side (functional matches).
    "vil_chat_agent": ("village", "chat_messages speaker_type=agent only, 1-in-5", iter_vil_chat_agent),
    "vil_chat_all": ("village", "chat_messages all speakers 1-in-5 (contamination check)", iter_vil_chat_all),
    "vil_goals": ("village", "agent_goals name+short_name+description (33, all)", iter_vil_goals),
    "vil_code": ("village", "claude_code assistant messages 1-in-5 (nested text extracted)", iter_vil_code),
    "vil_computer_lex": ("village", "computer_use_turns agent_messages+output+error 1-in-20", iter_vil_computer_lex),
    "vil_memories": ("village", "agent_memories consolidated prose 1-in-10 (reference)", iter_vil_memories),
}

# Diagonal (function-matched) pairs for the comparison matrix.
DIAGONALS = [
    ("ours_wiki", "vil_chat_agent"),    # coordination <-> coordination
    ("ours_evals", "vil_goals"),        # task statements <-> task statements
    ("ours_gems_names", "vil_code"),    # code names <-> code
    ("ours_traces", "vil_computer_lex"),# behavioral traces <-> behavioral traces
]
# Contamination / robustness pairs.
OFF_DIAGONALS = [
    ("ours_wiki", "vil_chat_all"),      # user-row contamination check
    ("ours_traces_clean", "vil_computer_lex"),  # analyst-note-free traces
]


def build_partition(cur, name, side, source, factory, tokenizers):
    tf = {t: Counter() for t in tokenizers}
    df = {t: Counter() for t in tokenizers}
    bi = Counter()
    tri = Counter()
    n_docs = 0
    for _, text in factory():
        n_docs += 1
        words = tok_word(text)
        for b in word_ngrams(words, 2):
            bi[b] += 1
        for t3 in word_ngrams(words, 3):
            tri[t3] += 1
        for tname in tokenizers:
            toks = TOKENIZERS[tname](text)
            if not toks:
                continue
            c = Counter(toks)
            tf[tname].update(c)
            df[tname].update(c.keys())
    n_tokens = sum(tf["word"].values())
    cur.execute(
        "INSERT OR REPLACE INTO partitions(name, side, source, n_docs, n_tokens)"
        " VALUES (?,?,?,?,?)",
        (name, side, source, n_docs, n_tokens),
    )
    for tname in tokenizers:
        rows = [(name, tname, term, tf[tname][term], df[tname][term]) for term in tf[tname]]
        cur.executemany(
            "INSERT OR REPLACE INTO terms(partition, tokenizer, term, tf, df)"
            " VALUES (?,?,?,?,?)",
            rows,
        )
    for n, counter in ((2, bi), (3, tri)):
        rows = [(name, n, g, c) for g, c in counter.items()]
        cur.executemany(
            "INSERT OR REPLACE INTO ngrams(partition, n, gram, tf) VALUES (?,?,?,?)",
            rows,
        )
    return n_docs, n_tokens


def main():
    ap = argparse.ArgumentParser(description="Build v2 functionally-matched lexdb.")
    ap.add_argument("--db", default="lexdb_v2.sqlite")
    ap.add_argument("--partitions", default=",".join(PARTITIONS_V2))
    ap.add_argument("--tokenizers", default="word,subword,char4,funcwords")
    ap.add_argument("--skip-missing", action="store_true",
                    help="Skip village partitions whose source files are absent.")
    args = ap.parse_args()

    names = [p.strip() for p in args.partitions.split(",") if p.strip()]
    tokenizers = [t.strip() for t in args.tokenizers.split(",") if t.strip()]

    # Map partitions to required files; skip gracefully if download in flight.
    needs_file = {
        "vil_chat_agent": CHAT_PATH, "vil_chat_all": CHAT_PATH,
        "vil_goals": GOALS_PATH, "vil_code": CODE_PATH,
        "vil_computer_lex": COMPUTER_PATH, "vil_memories": MEMORIES_PATH,
    }
    if args.skip_missing:
        names = [n for n in names
                 if n not in needs_file or os.path.exists(needs_file[n])]
        print(f"Partitions after skip-missing: {names}", flush=True)

    con = sqlite3.connect(args.db)
    cur = con.cursor()
    cur.executescript(SCHEMA)
    for name in names:
        if name not in PARTITIONS_V2:
            sys.exit(f"Unknown partition: {name}")
        side, source, factory = PARTITIONS_V2[name]
        print(f"Building partition: {name} ...", flush=True)
        n_docs, n_tokens = build_partition(cur, name, side, source, factory, tokenizers)
        con.commit()
        print(f"  docs={n_docs} tokens={n_tokens}", flush=True)
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
                ("build", "v2-functional"))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
                ("diagonals", json.dumps(DIAGONALS)))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
                ("strides", json.dumps(STRIDES)))
    con.commit()
    con.close()
    print(f"Wrote {args.db}")


if __name__ == "__main__":
    main()
