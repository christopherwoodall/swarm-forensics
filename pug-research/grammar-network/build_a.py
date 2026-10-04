#!/usr/bin/env python3
"""Build A: windowed co-occurrence grammar networks per text partition.

No POS tagger exists on this VM (no spacy/nltk), so the network is a
windowed co-occurrence graph over top-N terms -- a documented fallback, not
equivalent to dependency parsing. Partitions are compared on GRAPH metrics
(degree distribution, clustering, centrality, assortativity) plus tagger-free
structural prose features (sentence length, punctuation profile, list
markers, URL density, imperative frames). The question is structural
convergence where word counts found divergence.

Partitions (streamed, never fully loaded):
  wiki            collusion-wiki revision bodies (all)
  evals           DeepSearchQA questions (all 900)
  gems-code-nl    NL extracted from gem source (extract_code_text.py output)
  v-chat          AI Village chat_messages, speaker_type=agent (stride 5)
  v-mem           AI Village agent_memories (stride 20)
  v-goals         AI Village agent_goals name+description (all 33)
  v-code          AI Village claude_code_messages content (stride 5)
The traces URL-metadata partition is excluded: non-linguistic, Build B
territory. Documented in MODULE.md.

Output: networks.json, runs_log.jsonl. Run: python3 build_a.py
"""
import gzip
import json
import math
import re
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_RAW = HERE.parent / "stylometry" / "data" / "raw"
SILENT = Path("/home/hatch/workspace/silent-locus")
RUNS_LOG = HERE / "runs_log.jsonl"

TOP_N = 1500
WINDOW = 4
MIN_EDGE = 3  # min co-occurrence count for an edge

TOKEN = re.compile(r"[a-z0-9]+")
SENT_SPLIT = re.compile(r"[.!?]+\s+")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
LIST_RE = re.compile(r"(?m)^\s*(?:[-*#>]+|\d+[.)])\s+")
IMPERATIVES = {
    "use", "generate", "create", "fetch", "check", "run", "get", "set",
    "add", "make", "build", "test", "try", "see", "note", "find", "read",
    "write", "open", "call", "send", "return", "list", "show", "verify",
    "ensure", "update", "delete", "install", "start", "stop",
}
PUNCT = ".,:;!?-()[]\"'"


def tokenize(text):
    return TOKEN.findall(text.lower())


def claude_text(c):
    """Extract text from claude_code message content dicts."""
    out = []
    def walk(x):
        if isinstance(x, str):
            if len(x.strip()) > 2:
                out.append(x)
        elif isinstance(x, dict):
            for k in ("text", "content", "message", "input"):
                if k in x:
                    walk(x[k])
            # tool_use input params often carry NL
            if x.get("type") in ("tool_use",):
                walk(x.get("input"))
        elif isinstance(x, list):
            for i in x:
                walk(i)
    walk(c)
    return "\n".join(out)


def stream_docs(part):
    """Yield raw text docs for a partition, applying documented strides.
    Tolerates truncated gzip (agent_memories arrived cut); records it."""
    def gz_lines(p):
        try:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                for line in f:
                    yield line
        except EOFError:
            print(f"WARN truncated gzip tolerated: {p}", flush=True)
    if part == "wiki":
        p = SILENT / "data/2026-05-17-collusion-wiki/raw/revisions.jsonl"
        with open(p, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("body"):
                    yield r["body"]
    elif part == "evals":
        p = SILENT / "data/2026-10-01-deepsearchqa/questions.jsonl"
        with open(p, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("problem"):
                    yield r["problem"]
    elif part == "gems-code-nl":
        p = HERE / "data/processed/gems_code_nl.jsonl"
        if not p.exists():
            # gems partition under audit; may be removed. Skip, don't crash.
            print("SKIP gems-code-nl: source missing (logged, not an error)",
                  flush=True)
            return
        with open(p, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("text"):
                    yield r["text"]
    elif part == "v-chat":
        yield from _v_chat()
    elif part == "v-mem":
        p = DATA_RAW / "agent_memories.jsonl.gz"
        for i, line in enumerate(gz_lines(p)):
            if i % 20:
                continue
            r = json.loads(line)
            if r.get("content"):
                yield r["content"]
    elif part == "v-goals":
        p = DATA_RAW / "agent_goals.jsonl.gz"
        for line in gz_lines(p):
            r = json.loads(line)
            t = " ".join(x for x in (r.get("name"), r.get("description")) if x)
            if t:
                yield t
    elif part == "v-code":
        p = DATA_RAW / "claude_code_messages.jsonl.gz"
        for i, line in enumerate(gz_lines(p)):
            if i % 5:
                continue
            r = json.loads(line)
            t = claude_text(r.get("content"))
            if t.strip():
                yield t
    else:
        raise ValueError(part)


def _v_chat():
    p = DATA_RAW / "chat_messages.jsonl.gz"
    def gz_lines_local(pp):
        try:
            with gzip.open(pp, "rt", encoding="utf-8") as f:
                for line in f:
                    yield line
        except EOFError:
            print(f"WARN truncated gzip tolerated: {pp}", flush=True)
    for i, line in enumerate(gz_lines_local(p)):
        if i % 5:
            continue
        r = json.loads(line)
        if r.get("speaker_type") == "agent" and r.get("content"):
            yield r["content"]


def structural_features(texts):
    """Tagger-free prose structure profile. texts: list of sampled docs."""
    n_docs = len(texts)
    sent_lens, punct = [], Counter()
    list_hits = url_hits = imp_hits = n_sent = 0
    caps = digits = chars = 0
    for t in texts:
        chars += len(t)
        caps += sum(1 for c in t if c.isupper())
        digits += sum(1 for c in t if c.isdigit())
        for ch in PUNCT:
            punct[ch] += t.count(ch)
        list_hits += len(LIST_RE.findall(t))
        url_hits += len(URL_RE.findall(t))
        for s in SENT_SPLIT.split(t):
            toks = tokenize(s)
            if not toks:
                continue
            n_sent += 1
            sent_lens.append(len(toks))
            if toks[0] in IMPERATIVES:
                imp_hits += 1
    per1k = lambda c: round(1000 * c / max(chars, 1), 3)
    return {
        "n_docs": n_docs,
        "n_sentences": n_sent,
        "sent_len_mean": round(statistics.mean(sent_lens) if sent_lens else 0, 2),
        "sent_len_std": round(statistics.pstdev(sent_lens) if sent_lens else 0, 2),
        "punct_per1k": {k: per1k(punct[k]) for k in PUNCT},
        "list_markers_per_doc": round(list_hits / max(n_docs, 1), 3),
        "urls_per_doc": round(url_hits / max(n_docs, 1), 3),
        "imperative_sent_rate": round(imp_hits / max(n_sent, 1), 4),
        "caps_ratio": round(caps / max(chars, 1), 4),
        "digit_ratio": round(digits / max(chars, 1), 4),
    }


def build_network(part, sample_texts):
    """Two-pass: term frequencies, then co-occurrence over top-N terms."""
    freq = Counter()
    for t in stream_docs(part):
        freq.update(tokenize(t))
    vocab = [w for w, _ in freq.most_common(TOP_N)]
    idx = {w: i for i, w in enumerate(vocab)}
    n = len(vocab)
    cooc = Counter()
    for t in stream_docs(part):
        toks = [x for x in tokenize(t) if x in idx][:4000]
        for i, w in enumerate(toks):
            a = idx[w]
            for j in range(i + 1, min(i + 1 + WINDOW, len(toks))):
                b = idx[toks[j]]
                if a != b:
                    cooc[(min(a, b), max(a, b))] += 1
    # sparse weighted adjacency (undirected), thresholded
    adj = {}
    for (a, b), c in cooc.items():
        if c >= MIN_EDGE:
            adj.setdefault(a, {})[b] = float(c)
            adj.setdefault(b, {})[a] = float(c)
    deg = {i: sum(nbrs.values()) for i, nbrs in adj.items()}
    for i in range(n):
        deg.setdefault(i, 0.0)
    ecount = sum(len(nbrs) for nbrs in adj.values()) // 2
    m = sum(deg.values()) / 2  # weighted edge mass
    metrics = {
        "vocab_size": n,
        "edges": ecount,
        "density": round(2 * ecount / max(n * (n - 1), 1), 6),
        "mean_weighted_degree": round(sum(deg.values()) / max(n, 1), 2),
    }
    # degree-distribution power-law exponent (log-log CCDF least squares)
    ds = sorted((d for d in deg.values() if d > 0), reverse=True)
    if len(ds) > 20:
        xs = [math.log(d) for d in ds]
        ys = [math.log((i + 1) / len(ds)) for i in range(len(ds))]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        den = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0
        metrics["degree_ccdf_exponent"] = round(slope, 3)
    else:
        metrics["degree_ccdf_exponent"] = None
    # mean local clustering on top-500 by degree (neighbor-set intersections)
    topk = sorted(range(n), key=lambda i: deg[i], reverse=True)[:min(500, n)]
    bin_adj = {i: set(adj.get(i, ())) & set(topk) for i in topk}
    clusts = []
    for i in topk:
        nbrs = bin_adj[i]
        k = len(nbrs)
        if k < 2:
            clusts.append(0.0)
            continue
        e = sum(1 for u in nbrs for v in bin_adj[u] if v in nbrs) // 2
        clusts.append(2 * e / (k * (k - 1)))
    metrics["mean_clustering_top500"] = round(statistics.mean(clusts), 4) if clusts else 0.0
    # eigenvector centrality via sparse power iteration
    v = {i: 1.0 / n for i in range(n)}
    for _ in range(200):
        v_new = {}
        for i, nbrs in adj.items():
            s = 0.0
            for j, w in nbrs.items():
                s += w * v[j]
            v_new[i] = s
        norm = math.sqrt(sum(x * x for x in v_new.values()))
        if norm == 0:
            break
        for i in v_new:
            v_new[i] /= norm
        delta = math.sqrt(sum((v_new.get(i, 0.0) - v.get(i, 0.0)) ** 2 for i in range(n)))
        v = v_new
        if delta < 1e-8:
            break
    top = sorted(range(n), key=lambda i: v.get(i, 0.0), reverse=True)[:20]
    metrics["top_central"] = [(vocab[i], round(v.get(i, 0.0), 5)) for i in top]
    # assortativity: Pearson of degrees at edge endpoints (unweighted)
    ea, eb = [], []
    for a, nbrs in adj.items():
        for b in nbrs:
            if b > a:
                ea.append(deg[a])
                eb.append(deg[b])
    if len(ea) > 10:
        ma, mb = statistics.mean(ea), statistics.mean(eb)
        cov = sum((x - ma) * (y - mb) for x, y in zip(ea, eb))
        va = sum((x - ma) ** 2 for x in ea)
        vb = sum((y - mb) ** 2 for y in eb)
        r = cov / math.sqrt(va * vb) if va and vb else 0.0
        metrics["assortativity"] = round(r, 4)
    else:
        metrics["assortativity"] = None
    return metrics


def main():
    parts = ["wiki", "evals", "gems-code-nl", "v-chat", "v-mem", "v-goals", "v-code"]
    results = {"params": {"top_n": TOP_N, "window": WINDOW, "min_edge": MIN_EDGE,
                          "tagger": None, "note": "windowed co-occurrence fallback"},
               "partitions": {}}
    t0 = time.time()
    for part in parts:
        t1 = time.time()
        sample = []
        for i, t in enumerate(stream_docs(part)):
            if i < 400:
                sample.append(t[:4000])
        if not sample:
            results["partitions"][part] = {"status": "skipped_empty_source"}
            with open(RUNS_LOG, "a") as f:
                f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                    "run": "build_a", "partition": part,
                                    "status": "skipped_empty_source"}) + "\n")
            print(f"{part}: SKIPPED (empty source)", flush=True)
            continue
        net = build_network(part, sample)
        struct = structural_features(sample)
        results["partitions"][part] = {"network": net, "structure": struct}
        dt = time.time() - t1
        print(f"{part}: V={net['vocab_size']} E={net['edges']} "
              f"clust={net['mean_clustering_top500']} dt={dt:.1f}s", flush=True)
    with open(HERE / "networks.json", "w") as f:
        json.dump(results, f)
    with open(RUNS_LOG, "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                    "run": "build_a", "params": results["params"],
                                    "elapsed_s": round(time.time() - t0, 1),
                                    "status": "ok"}) + "\n")
    print(f"total {time.time()-t0:.1f}s -> networks.json")


if __name__ == "__main__":
    sys.exit(main())
