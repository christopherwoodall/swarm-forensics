#!/usr/bin/env python3
"""Prompt inversion: mine prompt-like content from AI Village tables,
characterize prompt->behavior mapping, invert to the OpenAI holdout.

Standard library only. CLI: --mode {mine,map,invert,all} (default all).
Outputs next to this script: prompt_mine.jsonl, prompt_map.json,
prompt_inferences.jsonl. Writeup: PROMPT_INVERSION.md (written separately).

Sampling: agent_memories.jsonl.gz is ~1.9G compressed; mine/map stream it
with a deterministic stride (STRIDE_MEM) so `make goal-invert` finishes.
The stride is recorded in every output file.
"""

import argparse
import gzip
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(REPO, "pug-research", "stylometry", "data", "raw")
SILENT = "/home/hatch/workspace/silent-locus"

STRIDE_MEM = 5      # 1-in-5 rows of agent_memories
STRIDE_CHAT = 5     # 1-in-5 rows of chat_messages
STRIDE_TRACE = 20   # 1-in-20 rows of traces.jsonl
STRIDE_WIKI = 50    # 1-in-50 rows of wiki revisions
CONTENT_CAP = 20000  # chars examined per memory record

MINE_OUT = os.path.join(HERE, "prompt_mine.jsonl")
MAP_OUT = os.path.join(HERE, "prompt_map.json")
INFER_OUT = os.path.join(HERE, "prompt_inferences.jsonl")

# ---------------------------------------------------------------- extraction

IDENT_RE = re.compile(
    r"(?im)^\s*(?:[-*\u2022]\s*)?(identity|i am|who i am)\s*[:\-\u2013]\s*(.{4,300})$")
MISSION_RE = re.compile(
    r"(?im)^\s*(?:[-*\u2022]\s*)?(personal goal|my goal|mission|objective|meta-?goal|purpose|assigned goal|village meta-?goal)\s*[:\-\u2013]\s*(.{4,300})$")
GUARD_RE = re.compile(
    r"(?im)^\s*(?:[-*\u2022]|\d+[.)])\s*((?:do not|don't|never|must not|always|must|prohibited|forbidden|avoid|requires?|no |opt-|reversible|ethical|privacy)[^\n]{5,280})$")
TOOL_RE = re.compile(
    r"(?im)^\s*(?:[-*\u2022]\s*)?(tools?|infra(?:structure)?|stack|tooling|computer)\s*[:\-\u2013]\s*(.{4,300})$")
SCHED_RE = re.compile(
    r"(?im)^\s*(?:[-*\u2022]\s*)?(hours|schedule|working hours)\s*[:\-\u2013]\s*(.{4,200})$")

ELEMENT_RES = [
    ("identity", IDENT_RE),
    ("mission", MISSION_RE),
    ("guardrail", GUARD_RE),
    ("tool", TOOL_RE),
    ("schedule", SCHED_RE),
]


def clean(s):
    s = re.sub(r"\s+", " ", s).strip()
    return s[:300]


def mine_memories(path, stride):
    """Yield {agent_id, element, text, source} rows."""
    n_in = n_out = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if n_in % stride:
                n_in += 1
                continue
            n_in += 1
            try:
                r = json.loads(line)
            except Exception:
                continue
            c = (r.get("content") or "")[:CONTENT_CAP]
            if not c:
                continue
            aid = r.get("agent_id")
            seen = set()
            for el, rx in ELEMENT_RES:
                for m in rx.finditer(c):
                    t = clean(m.group(m.lastindex))
                    key = (el, t[:80])
                    if key in seen or len(t) < 8:
                        continue
                    seen.add(key)
                    n_out += 1
                    yield {"agent_id": aid, "element": el, "text": t,
                           "source": "agent_memories"}
    sys.stderr.write(f"mine: scanned {n_in} memory rows, emitted {n_out}\n")


def mine_goals(path):
    n = 0
    try:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                n += 1
                name = r.get("name") or ""
                desc = r.get("description") or ""
                txt = clean(name + (" | " + desc if desc else ""))
                if txt:
                    yield {"agent_id": None, "element": "task_framing",
                           "text": txt, "source": "agent_goals",
                           "short_name": r.get("short_name")}
    except FileNotFoundError:
        sys.stderr.write("mine: agent_goals not present, skipping\n")
    sys.stderr.write(f"mine: {n} goal rows\n")


def cmd_mine():
    n = 0
    with open(MINE_OUT, "w", encoding="utf-8") as out:
        mem = os.path.join(RAW, "agent_memories.jsonl.gz")
        if os.path.exists(mem):
            for row in mine_memories(mem, STRIDE_MEM):
                out.write(json.dumps(row) + "\n")
                n += 1
        for row in mine_goals(os.path.join(RAW, "agent_goals.jsonl.gz")):
            out.write(json.dumps(row) + "\n")
            n += 1
    sys.stderr.write(f"mine: wrote {n} rows -> {MINE_OUT} "
                     f"(stride_mem={STRIDE_MEM})\n")

# ---------------------------------------------------------------- behavior

HEDGE = {"maybe", "might", "perhaps", "could", "possibly", "seemingly",
         "arguably", "likely", "probably"}
FIRSTP = {"i", "my", "me", "we", "our", "us", "mine", "ours"}
IMPER = {"use", "run", "check", "fetch", "get", "do", "make", "create",
         "write", "read", "open", "start", "stop", "set", "add", "list",
         "show", "find", "verify", "ensure", "try", "call", "send", "post"}
WORD_RE = re.compile(r"[a-z0-9']+")


def markers_of(texts):
    toks, lines = [], []
    for t in texts:
        tl = t.lower()
        toks.extend(WORD_RE.findall(tl))
        lines.extend(t.split("\n"))
    n_tok = len(toks) or 1
    n_lin = len(lines) or 1
    url = sum(1 for t in texts if "http" in t.lower())
    imper = sum(1 for ln in lines
                if ln.strip().split(" ", 1)[:1]
                and ln.strip().split(" ", 1)[0].lower().strip(".,:") in IMPER)
    hedged = sum(1 for w in toks if w in HEDGE)
    fp = sum(1 for w in toks if w in FIRSTP)
    listed = sum(1 for ln in lines
                 if re.match(r"\s*(?:[-*\u2022]|\d+[.)])\s+\S", ln))
    return {
        "n_msgs": len(texts),
        "mean_len": sum(len(t) for t in texts) / (len(texts) or 1),
        "url_rate": url / (len(texts) or 1),
        "imperative_rate": imper / n_lin,
        "hedge_rate": hedged / n_tok,
        "firstp_rate": fp / n_tok,
        "list_rate": listed / n_lin,
        "lex_div": len(set(toks)) / n_tok,
    }


def cmd_map():
    # per-agent prompt elements
    elems = defaultdict(set)
    with open(MINE_OUT, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("agent_id"):
                elems[r["agent_id"]].add(r["element"])
    # per-agent behavior from agent chat
    texts = defaultdict(list)
    n_in = 0
    chat = os.path.join(RAW, "chat_messages.jsonl.gz")
    with gzip.open(chat, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if n_in % STRIDE_CHAT:
                n_in += 1
                continue
            n_in += 1
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("speaker_type") != "agent":
                continue
            c = r.get("content") or ""
            if c.strip():
                texts[r.get("agent_speaker_id")].append(c[:2000])
    behav = {a: markers_of(t) for a, t in texts.items() if len(t) >= 3}
    sys.stderr.write(f"map: {len(behav)} agents with >=3 sampled messages\n")

    assoc = {}
    for el in ["identity", "mission", "guardrail", "tool", "schedule"]:
        with_el = [a for a in behav if el in elems.get(a, ())]
        without = [a for a in behav if el not in elems.get(a, ())]
        if not with_el or not without:
            continue
        marks = {}
        for m in ["mean_len", "url_rate", "imperative_rate", "hedge_rate",
                  "firstp_rate", "list_rate", "lex_div"]:
            w = sum(behav[a][m] for a in with_el) / len(with_el)
            wo = sum(behav[a][m] for a in without) / len(without)
            marks[m] = {"with_mean": round(w, 4), "without_mean": round(wo, 4),
                        "delta": round(w - wo, 4)}
        assoc[el] = {"n_with": len(with_el), "n_without": len(without),
                     "markers": marks}
    result = {"stride_mem": STRIDE_MEM, "stride_chat": STRIDE_CHAT,
              "n_agents_behavior": len(behav),
              "n_agents_mined": len(elems),
              "associations": assoc,
              "note": ("Within-village associations only. Guardrail-bearing "
                       "agents are rare; deltas are descriptive, not causal.")}
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    sys.stderr.write(f"map: wrote {MAP_OUT}\n")

# ---------------------------------------------------------------- invert

RELAY_HOSTS = ("jina.ai", "allorigins", "cors.lol", "da.gd", "r.jina")
ZZ_RE = re.compile(r"zz=oai\d+", re.I)
NONCE_RE = re.compile(r"[?=][0-9a-fx.]{12,}", re.I)
GOV_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:gov|edu)(?:\.au|\.uk)?\b", re.I)
API_RE = re.compile(r"/(?:api|v\d|rest|data|files|search|query)[/\?]", re.I)
PARAM_RE = re.compile(r"[?&]([a-zA-Z_][a-zA-Z0-9_]{1,30})=")
JQ_RE = re.compile(r"select\(|startswith\(|\.code\b|jq\b", re.I)


def infer_fragment(fid, partition, frag):
    """Evidence-grounded prompt-element hypotheses. Tier 1 = 2+ independent
    evidence types; Tier 2 = single; Tier 3 = speculative."""
    f = frag
    infs = []

    def add(element, value, tier, evidence):
        infs.append({"element": element, "value": value, "tier": tier,
                     "evidence": evidence})

    if ZZ_RE.search(f):
        add("bookkeeping", "tag every request with a session label",
            1, ["zz=oai<digits> present in URL",
                "label grammar zz=oai<epoch-ns>"])
    if any(h in f.lower() for h in RELAY_HOSTS):
        hosts = sorted({h for h in RELAY_HOSTS if h in f.lower()})
        add("tool_use", "fetch via public relay/proxy ladder",
            1 if len(hosts) >= 2 else 2,
            ["relay host(s): " + ",".join(hosts),
             "multi-hop chain" if len(hosts) >= 2 else "single relay hop"])
    if GOV_RE.search(f) and (API_RE.search(f) or PARAM_RE.search(f)):
        dom = GOV_RE.search(f).group(0)
        add("role", "retrieve structured data from government API", 2,
            ["target domain: " + dom,
             "API-shaped path/query"])
    if JQ_RE.search(f):
        add("tool_use", "server-side filtering of fetched data", 2,
            ["jq filter syntax in fragment"])
    if NONCE_RE.search(f):
        add("bookkeeping", "cache-bust each request with a unique nonce", 2,
            ["nonce-shaped query token"])
    if len(infs) >= 2:
        add("mission", "complete a data-retrieval task end to end", 3,
            ["multiple tool/bookkeeping markers co-occur"])
    if not infs:
        add("guardrails", "no target-sensitivity guardrail evidenced", 3,
            ["fragment shows probing-shaped construction, "
             "no refusal/consent language"])
    return infs


def frag_traces(limit=400):
    p = os.path.join(SILENT, "openai-agent-traces/data/traces.jsonl")
    out, n = [], 0
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            if n % STRIDE_TRACE:
                n += 1
                continue
            n += 1
            try:
                r = json.loads(line)
            except Exception:
                continue
            u = r.get("source_url") or ""
            if u:
                out.append(("trace", r.get("trace_id", f"t{n}"), u[:400]))
            if len(out) >= limit:
                break
    return out


def frag_wiki(limit=400):
    p = os.path.join(SILENT, "data/2026-05-17-collusion-wiki/raw/revisions.jsonl")
    out, n = [], 0
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            if n % STRIDE_WIKI:
                n += 1
                continue
            n += 1
            try:
                r = json.loads(line)
            except Exception:
                continue
            b = (r.get("body") or "").strip()
            if len(b) >= 60:
                out.append(("wiki", str(r.get("rev_id", f"w{n}")),
                            b[:500]))
            if len(out) >= limit:
                break
    return out


def frag_gems(limit=700):
    p = os.path.join(SILENT, "data/processed/gems")
    out = []
    try:
        for d in sorted(os.listdir(p))[:limit]:
            out.append(("gems", d, d))
    except FileNotFoundError:
        pass
    return out


def cmd_invert():
    frags = frag_traces() + frag_wiki() + frag_gems()
    n = 0
    with open(INFER_OUT, "w", encoding="utf-8") as out:
        for part, fid, frag in frags:
            infs = infer_fragment(fid, part, frag)
            out.write(json.dumps({"id": fid, "partition": part,
                                  "fragment": frag[:300],
                                  "inferences": infs}) + "\n")
            n += 1
    sys.stderr.write(f"invert: {n} fragments -> {INFER_OUT}\n")

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", default="all",
                    choices=["mine", "map", "invert", "all"])
    args = ap.parse_args(argv)
    if args.mode in ("mine", "all"):
        cmd_mine()
    if args.mode in ("map", "all"):
        if not os.path.exists(MINE_OUT):
            sys.stderr.write("map: prompt_mine.jsonl missing, run --mode mine\n")
            sys.exit(2)
        cmd_map()
    if args.mode in ("invert", "all"):
        cmd_invert()


if __name__ == "__main__":
    main()
