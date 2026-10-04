#!/usr/bin/env python3
"""Build B: the hunt's URL/request construction grammar as a typed graph.

Nodes are URL components, not words: hosts, relay hosts, path-segment
grammars, query-param names, nonce/tag templates, jq ops. Edges are
observed co-occurrence within one request and nesting transitions
(relay wrapping chains). This graph IS the harness/toolkit fingerprint:
what stays constant while tasks and vocabulary change.

Sources (read-only): openai-agent-traces/data/traces.jsonl (1-in-20 stride),
the relay/proxy/archive term table from stylometry/REPORT.md, and the
4-layer laundering chain documented in jqp-ihme-lead.md:
  sec.gov -> allorigins.hexlet.app -> da.gd/4qPkK -> jqp.vercel.app+jq(MA) -> da.gd/Di7Cu

Output: request_grammar.json. Run: python3 build_b.py
"""
import gzip
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, unquote

HERE = Path(__file__).resolve().parent
SILENT = Path("/home/hatch/workspace/silent-locus")
TRACES = SILENT / "openai-agent-traces/data/traces.jsonl"
LEAD = Path("/home/hatch/workspace/silent-locus/collections/hunt-missed-surfaces"
            "/incident-discovery/jqp-ihme-lead.md")

RELAY_HOSTS = {
    "r.jina.ai", "allorigins.hexlet.app", "allorigins.win", "jqp.vercel.app",
    "api.cors.lol", "platform.lemino.ai", "da.gd", "web.archive.org",
    "arquivo.pt", "corsproxy.io", "api.allorigins.win", "thingproxy.freeboard.io",
    "cors.isomorphic-git.org", "proxy.cors.sh",
}
WAYBACK_HOSTS = {"web.archive.org", "arquivo.pt"}

NONCE_A = re.compile(r"[?&]x=0\.\d{10,}")          # ?x=0.<17 digits>
NONCE_BARE = re.compile(r"[?&](\d{10,}\.\d+)")     # ?0.<16 digits>
ZZ_OAI = re.compile(r"[?&]zz=oai\d+")
DOUBLE_SCHEME = re.compile(r"https?://https?://")
PCT26 = re.compile(r"%26")
CACHEBUST = re.compile(r"[?&]_=\d+")
NESTED_URL = re.compile(r"https?://[^\s'\"<>]+")
JQ_OPS = ["select(", "startswith(", "endswith(", "contains(", ".code",
          ".regCF_county_2019", "|", "jq="]


def classify_host(host):
    h = host.lower().lstrip("www.")
    if h in RELAY_HOSTS:
        return "relay"
    return "host"


def path_grammar(seg):
    if re.fullmatch(r"\d+", seg):
        return "{id}"
    if re.fullmatch(r"[0-9a-f-]{20,}", seg):
        return "{hexid}"
    if re.fullmatch(r"0\.\d{10,}", seg):
        return "{nonce}"
    return seg.lower()


def parse_request(url):
    """Return (nodes, chain_edges) for one request URL."""
    nodes, chain = [], []
    if DOUBLE_SCHEME.search(url):
        nodes.append(("template", "T_DOUBLE_SCHEME"))
        url = DOUBLE_SCHEME.sub("http://", url, count=1)
    if PCT26.search(url):
        nodes.append(("template", "T_PCT26"))
    # nesting: every embedded URL is a chain hop. finditer catches inner
    # scheme occurrences that a greedy whole-string match would swallow
    # (e.g. r.jina.ai/http://https://target -> jina.ai, target).
    # Unquote first: relay nesting is routinely percent-encoded
    # (jqp?url=https%3A%2F%2Fmd.succ.ai%2F...).
    hosts_in_order = []
    for m in re.finditer(r"https?://", unquote(url)):
        inner = unquote(url)[m.start():]
        try:
            h = urlparse(inner).hostname or ""
        except ValueError:
            continue
        h = h.lower()
        if h and h not in hosts_in_order:
            hosts_in_order.append(h)
    for h in hosts_in_order:
        nodes.append((classify_host(h), h))
    for a, b in zip(hosts_in_order, hosts_in_order[1:]):
        chain.append((a, b))  # outer -> inner
    try:
        p = urlparse(url)
    except ValueError:
        return nodes, chain
    host = (p.hostname or "").lower()
    for seg in p.path.split("/"):
        if seg:
            nodes.append(("pathseg", f"{host}:{path_grammar(seg)}"))
    try:
        params = parse_qsl(p.query, keep_blank_values=True)
    except ValueError:
        params = []
    for k, v in params:
        nodes.append(("param", k))
    q = p.query
    if re.search(r"zz=oai\d+", q):
        nodes.append(("template", "T_ZZ_OAI"))
    if NONCE_A.search(q):
        nodes.append(("template", "T_NONCE_A"))
    if CACHEBUST.search(q):
        nodes.append(("template", "T_CACHEBUST"))
    if NONCE_BARE.search(p.query):
        nodes.append(("template", "T_NONCE_BARE"))
    for op in JQ_OPS:
        if op in url:
            nodes.append(("jqop", op))
    return nodes, chain


def iter_trace_urls():
    opener = gzip.open if str(TRACES).endswith(".gz") else open
    with opener(TRACES, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % 20:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("source_url"):
                yield r["source_url"], "traces"


def iter_wiki_urls():
    """Secondary source: relay-wrapped URLs embedded in wiki revision bodies.
    The traces sample is direct-fetch dominated; the relay layer of the
    request grammar lives in the wiki corpus (the relay-vocabulary hub)."""
    p = SILENT / "data/2026-05-17-collusion-wiki/raw/revisions.jsonl"
    with open(p, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % 5:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            body = r.get("body") or ""
            for m in set(URL_IN_TEXT.findall(body)):
                yield m, "wiki"


URL_IN_TEXT = re.compile(r"https?://[^\s'\"<>\]\)]+")

def main():
    t0 = time.time()
    node_w = Counter()
    edge_w = Counter()   # co-occurrence within a request
    chain_w = Counter()  # nesting transitions outer->inner
    src_w = Counter()
    n_req = 0

    def ingest(url):
        nodes, chain = parse_request(url)
        seen = sorted(set(nodes))
        for n in nodes:
            node_w[n] += 1
        for a_i in range(len(seen)):
            for b_i in range(a_i + 1, len(seen)):
                edge_w[(seen[a_i], seen[b_i])] += 1
        for a, b in chain:
            chain_w[(a, b)] += 1

    for url, _ in iter_trace_urls():
        n_req += 1
        src_w["traces"] += 1
        ingest(url)
    for url, _ in iter_wiki_urls():
        n_req += 1
        src_w["wiki"] += 1
        ingest(url)

    # documented motifs from the lead doc (not re-derived here)
    motifs = [
        {"name": "sec-4layer-laundering",
         "chain": ["www.sec.gov", "allorigins.hexlet.app", "da.gd",
                   "jqp.vercel.app", "da.gd"],
         "note": "target -> CORS relay -> shortener -> jq-proxy(MA filter) "
                 "-> shortener; from jqp-ihme-lead.md"},
        {"name": "jqp-ihme-anemia",
         "chain": ["vizhub.healthdata.org", "jqp.vercel.app"],
         "note": "jqp/api/v0?url= wrapping IHME anemia API; da.gd/iar2 "
                 "302s to the same jqp URL (short+full dual submission)"},
    ]
    by_type = Counter()
    for (t, _), c in node_w.items():
        by_type[t] += c
    top_nodes = {}
    for t in ("host", "relay", "pathseg", "param", "template", "jqop"):
        top_nodes[t] = [(n, c) for (tt, n), c in node_w.most_common()
                        if tt == t][:15]
    top_chains = [((a, b), c) for (a, b), c in chain_w.most_common(20)]
    out = {
        "params": {"stride": 20, "n_requests": n_req},
        "node_mass_by_type": dict(by_type),
        "top_nodes_by_type": top_nodes,
        "top_nesting_chains": top_chains,
        "documented_motifs": motifs,
        "fingerprint": {
            "nonce_templates": {t: node_w[("template", t)] for t in
                                ("T_NONCE_A", "T_NONCE_BARE", "T_ZZ_OAI",
                                 "T_DOUBLE_SCHEME", "T_PCT26", "T_CACHEBUST")},
            "relay_mass": sum(c for (t, _), c in node_w.items() if t == "relay"),
            "n_distinct_relays": len({n for (t, n) in node_w if t == "relay"}),
        },
    }
    with open(HERE / "request_grammar.json", "w") as f:
        json.dump(out, f)
    with open(HERE / "runs_log.jsonl", "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "run": "build_b", "params": out["params"],
                            "elapsed_s": round(time.time() - t0, 1),
                            "status": "ok"}) + "\n")
    print(f"requests={n_req} nodes={len(node_w)} edges={len(edge_w)} "
          f"chains={len(chain_w)} dt={time.time()-t0:.1f}s")


if __name__ == "__main__":
    sys.exit(main())
