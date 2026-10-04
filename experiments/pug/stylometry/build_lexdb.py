#!/usr/bin/env python3
"""Build a partitioned lexical database from agent-text corpora.

Each partition keeps its own term frequencies. Partitions never merge.
The database supports pairwise stylometric comparison across partitions.

Usage:
    python build_lexdb.py --db lexdb.sqlite
    python build_lexdb.py --db lexdb.sqlite --partitions gems,wiki --tokenizers word,funcwords

Conventions:
- Read silent-locus data read-only. Never write outside this directory.
- Stream large files line by line. Never load a full table into memory.
- Record every sampling decision in the `meta` table and in README.md.
"""

import argparse
import gzip
import json
import os
import re
import sqlite3
import sys
from collections import Counter
from urllib.parse import unquote

# Absolute paths to read-only source data. Do not modify these files.
SILENT_LOCUS = os.path.expanduser("~/workspace/silent-locus")
GEMS_DIR = os.path.join(SILENT_LOCUS, "data/processed/gems")
TRACES_PATH = os.path.join(SILENT_LOCUS, "openai-agent-traces/data/traces.jsonl")
WIKI_REV_PATH = os.path.join(
    SILENT_LOCUS, "data/2026-05-17-collusion-wiki/raw/revisions.jsonl"
)
DSQA_PATH = os.path.join(SILENT_LOCUS, "data/2026-10-01-deepsearchqa/questions.jsonl")

WORD_RE = re.compile(r"[a-z0-9]+")


def _pre(text):
    """Percent-decode before tokenizing.

    Documented choice (adversarial fix): decode-then-split, not atomic %XX
    units. %3A becomes ':' (a separator), so URL-encoded bytes never surface
    as hex-fragment tokens ('3a', '2f'). Applied to every tokenizer.
    """
    try:
        return unquote(text, errors="replace")
    except Exception:
        return text


# Agent-naming morphemes observed in gem directory names. Used only for
# greedy splitting of long (>=10 char) tokens, where whole-word
# tokenization provably merges agent morphemes (e.g. 'agentoaitestabc123').
# Derived from the gem dirname vocabulary; documented heuristic, not a model.
MORPHEMES = frozenset(
    """oai zz zzz test fetch proxy probe query lambda lamb jan abc xyz agent gem
    chat ai api json url web hook scan dlx civic council design hack crawl scrape
    runner exfil doc html meta demo fossil bzr hg git svn vcs south london yard
    wand news meet vanity controller exp fmt result cal data bot net token key id
    db sql http rest xml csv""".split()
)
_MORPH_BY_LEN = sorted(MORPHEMES, key=len, reverse=True)


def _morpheme_split(tok):
    """Greedy longest-match split of a long token on known morphemes."""
    out = []
    buf = []
    i, n = 0, len(tok)
    while i < n:
        hit = None
        for m in _MORPH_BY_LEN:
            if tok.startswith(m, i):
                hit = m
                break
        if hit:
            if buf:
                out.append("".join(buf))
                buf = []
            out.append(hit)
            i += len(hit)
        else:
            buf.append(tok[i])
            i += 1
    if buf:
        out.append("".join(buf))
    return out


def tok_word(text):
    """Lowercase alphanumeric word tokens (percent-decoded first)."""
    return WORD_RE.findall(_pre(text).lower())


def tok_subword(text):
    """Subword tokens: case/digit/separator splits + morpheme splitting.

    'agentoaitestabc123' -> ['agent','oai','test','abc','123'].
    Morpheme splitting applies only to tokens >= 10 chars, so ordinary
    English words ('latest', 'proxy' is 5) are never over-split.
    """
    text = _pre(text)
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", "\x00", text)
    text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "\x00", text)
    text = re.sub(r"(?<=[A-Za-z])(?=[0-9])", "\x00", text)
    text = re.sub(r"(?<=[0-9])(?=[A-Za-z])", "\x00", text)
    out = []
    for chunk in text.split("\x00"):
        for tok in WORD_RE.findall(chunk.lower()):
            if len(tok) >= 10:
                out.extend(_morpheme_split(tok))
            else:
                out.append(tok)
    return out

# Closed class of English function words. Used for the funcwords tokenizer.
# Style signal lives in function words. Topic signal lives in content words.
FUNCTION_WORDS = frozenset(
    """a about above after again against all am an and any are as at be because been
    before being below between both but by can cannot could did do does doing down
    during each few for from further had has have having he her here hers herself
    him himself his how i if in into is it its itself me more most my myself no nor
    not of off on once only or other ought our ours ourselves out over own same she
    should so some such than that the their theirs them themselves then there these
    they this those through to too under until up very was we were what when where
    which while who whom why will with would you your yours yourself yourselves""".split()
)


def tok_char4(text):
    """Character 4-grams over compacted lowercase text (percent-decoded first)."""
    s = re.sub(r"\s+", " ", _pre(text).lower()).strip()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return [s[i : i + 4] for i in range(len(s) - 3)] if len(s) >= 4 else []


def tok_funcwords(text):
    """Function words only. Drops topic vocabulary."""
    return [t for t in tok_word(text) if t in FUNCTION_WORDS]


TOKENIZERS = {
    "word": tok_word,
    "subword": tok_subword,
    "char4": tok_char4,
    "funcwords": tok_funcwords,
}


# Directories excluded from every gems partition: third-party code, not
# agent-authored. oai-1.3.0 is the upstream OAI-PMH (Open Archives Initiative)
# Ruby library; its 800+ "oai" tokens are not OpenAI markers.
EXCLUDE_GEM_DIRS = frozenset({"oai-1.3.0"})


def iter_gems_names():
    """Yield (dirname, dirname) for each agent gem directory.

    The directory name is the agent-chosen signal. Whole-word tokenization
    could not split concatenated names; the subword tokenizer can.
    """
    for dirname in sorted(os.listdir(GEMS_DIR)):
        if dirname in EXCLUDE_GEM_DIRS:
            continue
        d = os.path.join(GEMS_DIR, dirname)
        if not os.path.isdir(d):
            continue
        yield dirname, dirname


def iter_gems_code():
    """Yield (dirname, file bodies) for each agent gem directory.

    DIAGNOSTIC ONLY. Audit result: 740 files, median 1 byte -- the agent gems
    are empty scaffolds. No agent-attributable signal survives the oai-1.3.0
    exclusion, so this partition is REMOVED from the final dataset after the
    Finding-1 diagnostic run. Kept here only to reproduce that diagnostic.
    """
    for dirname in sorted(os.listdir(GEMS_DIR)):
        if dirname in EXCLUDE_GEM_DIRS:
            continue
        d = os.path.join(GEMS_DIR, dirname)
        if not os.path.isdir(d):
            continue
        parts = []
        for root, _, files in os.walk(d):
            for fn in sorted(files):
                if fn.rsplit(".", 1)[-1].lower() in ("gemspec", "rb", "md", "txt", "gemfile"):
                    p = os.path.join(root, fn)
                    try:
                        with open(p, "r", errors="replace") as f:
                            parts.append(f.read())
                    except OSError:
                        continue
        yield dirname, "\n".join(parts)


def iter_gems():
    """Legacy mixed partition. SUPERSEDED by iter_gems_names/_code split.

    Kept for provenance only; do not use in new comparisons.
    """
    for dirname in sorted(os.listdir(GEMS_DIR)):
        d = os.path.join(GEMS_DIR, dirname)
        if not os.path.isdir(d):
            continue
        parts = [dirname]
        for root, _, files in os.walk(d):
            for fn in sorted(files):
                if fn.rsplit(".", 1)[-1].lower() in ("gemspec", "rb", "md", "txt", "gemfile"):
                    p = os.path.join(root, fn)
                    try:
                        with open(p, "r", errors="replace") as f:
                            parts.append(f.read())
                    except OSError:
                        continue
        yield dirname, "\n".join(parts)


def iter_traces(stride=20):
    """Yield (doc_id, text) for a systematic sample of trace records.

    Sampling rule: every 20th line (5%). Deterministic. Documented.
    Text fields: source_url, query parameter names and values, analyst note.
    """
    idx = 0
    kept = 0
    with open(TRACES_PATH, "r", errors="replace") as f:
        for line in f:
            idx += 1
            if idx % stride != 0:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            parts = [d.get("source_url") or ""]
            feat = d.get("features") or {}
            parts.append(" ".join(feat.get("query_param_names") or []))
            nqp = d.get("notable_query_params") or {}
            if isinstance(nqp, dict):
                parts.append(" ".join(f"{k} {v}" for k, v in nqp.items()))
            attr = d.get("attribution") or {}
            parts.append(attr.get("note") or "")
            parts.append(" ".join(d.get("tags") or []))
            kept += 1
            yield d.get("trace_id") or f"line-{idx}", "\n".join(parts)
    iter_traces.n_docs = kept
    iter_traces.n_lines = idx


def iter_traces_clean(stride=20):
    """Yield (doc_id, text) for the URL+params-only trace sample.

    Adversarial fix (#11): the standard traces partition mixes analyst voice
    (attribution notes, tags) into agent-behavior text. This partition keeps
    only source_url and query parameter names/values -- the agent-attributable
    part. Findings computed on traces/ must be re-run here and both reported.
    """
    idx = 0
    with open(TRACES_PATH, "r", errors="replace") as f:
        for line in f:
            idx += 1
            if idx % stride != 0:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            parts = [d.get("source_url") or ""]
            feat = d.get("features") or {}
            parts.append(" ".join(feat.get("query_param_names") or []))
            nqp = d.get("notable_query_params") or {}
            if isinstance(nqp, dict):
                parts.append(" ".join(f"{k} {v}" for k, v in nqp.items()))
            yield d.get("trace_id") or f"line-{idx}", "\n".join(parts)


def iter_wiki():
    """Yield (rev_id, body) for every collusion-wiki revision.

    Bodies are raw wiki markup. No cleaning. Cleaning would hide the signal.
    """
    with open(WIKI_REV_PATH, "r", errors="replace") as f:
        for i, line in enumerate(f):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            yield d.get("rev_id") or f"rev-{i}", d.get("body") or ""


def iter_evals():
    """Yield (id, problem) for every DeepSearchQA question."""
    with open(DSQA_PATH, "r", errors="replace") as f:
        for i, line in enumerate(f):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            yield d.get("id") or f"dsqa-{i}", d.get("problem") or ""


# Registry: partition name -> (side, source description, iterator factory).
# 'gems' (mixed) is superseded; use gems_names. gems_code is diagnostic-only
# and removed from the final dataset per the partition audit.
PARTITIONS = {
    "gems_names": (
        "openai",
        "data/processed/gems dirnames only (agent-chosen names, oai-1.3.0 excluded)",
        iter_gems_names,
    ),
    "gems_code": (
        "openai",
        "DIAGNOSTIC ONLY: gem file bodies (audit: bust, removed from final dataset)",
        iter_gems_code,
    ),
    "traces": (
        "openai",
        "openai-agent-traces/data/traces.jsonl (systematic 1-in-20 sample, incl. analyst notes)",
        iter_traces,
    ),
    "traces_clean": (
        "openai",
        "traces.jsonl 1-in-20, URL+params only (no analyst notes/tags)",
        iter_traces_clean,
    ),
    "wiki": (
        "openai",
        "data/2026-05-17-collusion-wiki/raw/revisions.jsonl (all revision bodies)",
        iter_wiki,
    ),
    "evals": (
        "openai",
        "data/2026-10-01-deepsearchqa/questions.jsonl (900 eval questions)",
        iter_evals,
    ),
}


def word_ngrams(tokens, n):
    """Yield n-gram strings from a token list."""
    if len(tokens) < n:
        return
    for i in range(len(tokens) - n + 1):
        yield " ".join(tokens[i : i + n])


def build_partition(cur, name, side, source, factory, tokenizers):
    """Stream one partition into the database. Return doc/token counts."""
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
        rows = [
            (name, tname, term, tf[tname][term], df[tname][term])
            for term in tf[tname]
        ]
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


SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS partitions(
    name TEXT PRIMARY KEY, side TEXT, source TEXT, n_docs INT, n_tokens INT);
CREATE TABLE IF NOT EXISTS terms(
    partition TEXT, tokenizer TEXT, term TEXT, tf INT, df INT,
    PRIMARY KEY(partition, tokenizer, term));
CREATE TABLE IF NOT EXISTS ngrams(
    partition TEXT, n INT, gram TEXT, tf INT,
    PRIMARY KEY(partition, n, gram));
CREATE INDEX IF NOT EXISTS idx_terms_pt ON terms(partition, tokenizer, tf DESC);
"""


def main():
    ap = argparse.ArgumentParser(description="Build partitioned lexical database.")
    ap.add_argument("--db", default="lexdb.sqlite")
    # Diagnostic partitions (source startswith "DIAGNOSTIC") are excluded from
    # default builds; the audit removed them from the dataset.
    default_parts = [n for n in PARTITIONS
                     if not PARTITIONS[n][1].startswith("DIAGNOSTIC")]
    ap.add_argument("--partitions", default=",".join(default_parts),
                    help="Comma-separated partition names.")
    ap.add_argument("--tokenizers", default="word,char4,funcwords")
    args = ap.parse_args()

    names = [p.strip() for p in args.partitions.split(",") if p.strip()]
    tokenizers = [t.strip() for t in args.tokenizers.split(",") if t.strip()]
    for t in tokenizers:
        if t not in TOKENIZERS:
            sys.exit(f"Unknown tokenizer: {t}")

    db_exists = os.path.exists(args.db)
    con = sqlite3.connect(args.db)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    for name in names:
        if name not in PARTITIONS:
            sys.exit(f"Unknown partition: {name}")
        side, source, factory = PARTITIONS[name]
        print(f"Building partition: {name} ...", flush=True)
        n_docs, n_tokens = build_partition(cur, name, side, source, factory, tokenizers)
        con.commit()
        print(f"  docs={n_docs} tokens={n_tokens}", flush=True)

    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
                ("tokenizers", ",".join(tokenizers)))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
                ("traces_stride", "20"))
    con.commit()
    con.close()
    print(f"Wrote {args.db}" + (" (appended)" if db_exists else ""))


if __name__ == "__main__":
    main()
