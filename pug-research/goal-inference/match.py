#!/usr/bin/env python3
"""Fragment-to-goal matcher (degraded mode).

Design target (DESIGN.md / SOTA.md): bi-encoder retriever + cross-encoder
reranker. This VM has no sentence-transformers, no torch, and no PyPI.
Degraded mode: TF-IDF + cosine retriever with a transparent heuristic
rerank. The rerank is a documented formula, not a learned cross-encoder.
Nothing here pretends to be the SOTA stack.

Structured trace features are first-class inputs: query param names, URL
path grammar, domains, jq filter ops, relay hosts. They live in the same
TF-IDF space as word tokens, prefixed ``f:``.

Modes:
  loo       leave-one-out over the 900 DeepSearchQA questions (labeled proxy)
  anchored  two anchored sanity checks (DoE trace, MA-county jq filter)
  infer     holdout inference on wiki / traces / gems fragments
  all       loo + anchored + infer

Every run appends a parameter + metric record to runs.md.
"""

import argparse
import gzip
import json
import math
import os
import re
import sqlite3
import sys
import time
from collections import Counter

import numpy as np
from scipy import sparse

HERE = os.path.dirname(os.path.abspath(__file__))
LEXDB = os.path.join(HERE, "..", "stylometry", "lexdb.sqlite")
SILENT = "/home/hatch/workspace/silent-locus"
DSQA_PATH = os.path.join(SILENT, "data/2026-10-01-deepsearchqa/questions.jsonl")
TRACES_PATH = os.path.join(SILENT, "openai-agent-traces/data/traces.jsonl")
WIKI_REV_PATH = os.path.join(SILENT, "data/2026-05-17-collusion-wiki/raw/revisions.jsonl")
GEMS_ROOT = os.path.join(SILENT, "data/processed/gems")

WORD_RE = re.compile(r"[a-z0-9]+")
DOM_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:gov|org|com|edu|net|io|au|uk|dev|app)\b")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
CAP_RE = re.compile(r"\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,}){0,2}\b")

STOPWORDS = set(
    """a an the and or but of to in on for with as at by from is are was were be been
    being it its this that these those which what when where who whom whose how why
    not no nor do does did done have has had having will would can could should may
    might must shall i you he she we they them his her our your their my me him us
    so such than then there here than too very into over under between through during
    each other more most some any all both own same per via within without about
    against among""".split()
)

# VOCABULARY PROVENANCE (frozen v1, 2026-10-04): AGENCIES, RELAYS, and
# TRADE_TERMS were hand-compiled from prior hunt findings (the June 2026
# incident set: SEC/DoE/BEA/CDC/AIHW/UNCTAD targets and the jina/allorigins/
# jqp/wayback/arquivo relay ladder). This is test-set-informed feature
# engineering: a holdout trace touching a KNOWN incident agency gets
# features; a trace from a novel agency gets none. The matcher therefore
# cannot discover goals outside this vocabulary, and recall on novel
# agencies is unmeasured. Do not extend these sets without bumping the
# version note and re-running.
AGENCIES = {
    "sec", "doe", "bea", "cdc", "fbi", "doj", "census", "aihw", "unctad",
    "ihme", "oecd", "dhs", "epa", "nih", "nsf", "bls", "usda",
}

RELAYS = {
    "jina": "jina", "r.jina.ai": "jina",
    "allorigins": "allorigins", "allorigins.hexlet.app": "allorigins",
    "jqp": "jqp", "jqp.vercel.app": "jqp",
    "wayback": "wayback", "web.archive.org": "wayback",
    "arquivo": "arquivo", "arquivo.pt": "arquivo",
    "corsproxy": "corsproxy", "api.cors.lol": "corsproxy",
    "da.gd": "da.gd", "is.gd": "is.gd",
}

TRADE_TERMS = {
    "relay", "jina", "proxy", "proxies", "archive", "wayback", "task",
    "county", "counties", "sec", "json", "nonce", "zz",
}


# ---------------------------------------------------------------- tokenize

def tok_word(text):
    return WORD_RE.findall(text.lower())


def content_tokens(text):
    return [t for t in tok_word(text) if t not in STOPWORDS]


# ---------------------------------------------------------------- features

def features_from_url(url):
    feats = []
    if not url:
        return feats
    low = url.lower()
    m = re.search(r"https?://([^/]+)", low)
    if m:
        host = m.group(1)
        if host.startswith("www."):
            host = host[4:]
        feats.append("f:dom=" + host)
        rest = low[m.end():]
        path = rest.split("?")[0]
        for seg in path.strip("/").split("/"):
            seg = seg.strip()
            if seg and len(seg) < 40:
                feats.append("f:path=" + seg)
        q = rest.split("?", 1)
        if len(q) > 1:
            for pair in q[1].split("&"):
                name = pair.split("=")[0].strip()
                if name and len(name) < 40:
                    feats.append("f:param=" + name)
    for key, canon in RELAYS.items():
        if key in low:
            feats.append("f:relay=" + canon)
    return feats


def features_from_question(text):
    feats = []
    low = text.lower()
    for dom in set(DOM_RE.findall(low)):
        if dom.startswith("www."):
            dom = dom[4:]
        feats.append("f:dom=" + dom)
    for m in YEAR_RE.finditer(low):
        feats.append("f:year=" + m.group(0))
    words = set(tok_word(low))
    for ag in AGENCIES:
        if ag in words:
            feats.append("f:agency=" + ag)
    return feats


def features_from_jq(text):
    feats = []
    low = text.lower()
    if "select(" in low:
        feats.append("f:jq=select")
    if "startswith" in low:
        feats.append("f:jq=startswith")
    m = re.search(r'startswith\(\s*"([^"]+)"', low)
    if m:
        feats.append("f:filter=" + m.group(1).lower())
    return feats


def features_from_wiki(text):
    feats = []
    low = text.lower()
    for key, canon in RELAYS.items():
        if key in low:
            feats.append("f:relay=" + canon)
    for dom in set(DOM_RE.findall(low)):
        if dom.startswith("www."):
            dom = dom[4:]
        feats.append("f:dom=" + dom)
    return feats


# ---------------------------------------------------------------- vectors

class Matcher:
    """TF-IDF cosine retriever + heuristic rerank over word + feature tokens."""

    def __init__(self, lexdb_path, feat_weight=2.0):
        self.feat_weight = feat_weight
        self.vocab, self.idf = self._load_idf(lexdb_path)
        self.vindex = {t: i for i, t in enumerate(self.vocab)}

    def _load_idf(self, path):
        con = sqlite3.connect(path)
        df = Counter()
        n_docs = 0
        for (name, n) in con.execute("SELECT name, n_docs FROM partitions"):
            n_docs += n
        for (term, s) in con.execute(
            "SELECT term, SUM(df) FROM terms WHERE tokenizer='word' GROUP BY term"
        ):
            df[term] = s
        con.close()
        vocab = sorted(df)
        idf = np.array(
            [math.log((n_docs + 1) / (df[t] + 1)) + 1.0 for t in vocab],
            dtype=np.float64,
        )
        return vocab, idf

    def batch_matrix(self, docs):
        """docs: list of (tokens, feature_tokens).

        Stage 1 uses word TF-IDF only. Structured features are returned as
        counters and act in the stage-2 rerank, scaled by feat_weight.
        """
        rows, cols, data = [], [], []
        feat_counters = []
        for di, (tokens, feats) in enumerate(docs):
            tf = Counter(tokens)
            for t, c in tf.items():
                i = self.vindex.get(t)
                if i is not None:
                    rows.append(di)
                    cols.append(i)
                    data.append(c * self.idf[i])
            fc = Counter()
            for f, c in Counter(feats).items():
                fc[f] = c * self.feat_weight
            feat_counters.append(fc)
        X = sparse.csr_matrix(
            (np.array(data), (np.array(rows), np.array(cols))),
            shape=(len(docs), len(self.vocab)),
        )
        return X, feat_counters

    def index_goals(self, goal_docs):
        """Build goal matrices. Structured features are first-class: they get
        their own TF-IDF dimensions, with idf computed over the goal set.
        Returns (Xg, feat_vocab, feat_idf, g_feat_counters)."""
        Xw, g_feats = self.batch_matrix(goal_docs)
        fdf = Counter()
        for fc in g_feats:
            for f in fc:
                fdf[f] += 1
        n = len(goal_docs)
        feat_vocab = sorted(fdf)
        findex = {f: i for i, f in enumerate(feat_vocab)}
        feat_idf = np.array(
            [math.log((n + 1) / (fdf[f] + 1)) + 1.0 for f in feat_vocab])
        rows, cols, data = [], [], []
        for di, fc in enumerate(g_feats):
            for f, c in fc.items():
                rows.append(di)
                cols.append(findex[f])
                data.append(c * feat_idf[findex[f]])
        Xf = sparse.csr_matrix(
            (np.array(data), (np.array(rows), np.array(cols))),
            shape=(n, len(feat_vocab)))
        return (sparse.hstack([Xw, Xf]).tocsr(), feat_vocab, feat_idf,
                g_feats)

    def vectorize_queries(self, q_docs, feat_vocab, feat_idf):
        Xw, q_feats = self.batch_matrix(q_docs)
        findex = {f: i for i, f in enumerate(feat_vocab)}
        rows, cols, data = [], [], []
        for di, fc in enumerate(q_docs):
            for f, c in Counter(fc[1]).items():
                if f in findex:
                    rows.append(di)
                    cols.append(findex[f])
                    data.append(c * self.feat_weight * feat_idf[findex[f]])
        Xf = sparse.csr_matrix(
            (np.array(data), (np.array(rows), np.array(cols))),
            shape=(len(q_docs), len(feat_vocab)))
        return sparse.hstack([Xw, Xf]).tocsr(), q_feats

    @staticmethod
    def _norm(X):
        n = np.sqrt(X.multiply(X).sum(axis=1)).A.ravel()
        n[n == 0] = 1.0
        return X.multiply(1.0 / n[:, None]).tocsr()

    def cosine_topk(self, Xq, Xg, k=20):
        Xn, Gn = self._norm(Xq), self._norm(Xg)
        S = (Xn * Gn.T).toarray()
        idx = np.argsort(-S, axis=1)[:, :k]
        return S, idx

    FEAT_TYPE_W = {"f:dom": 3.0, "f:param": 2.0, "f:agency": 2.0,
                   "f:jq": 2.0, "f:filter": 2.0, "f:path": 1.5,
                   "f:year": 1.0, "f:relay": 1.0, "f:gem": 0.5}

    def rerank(self, q_feats, g_feats_list, cos_scores, w_cos=0.6, w_feat=0.4):
        """Transparent heuristic rerank. NOT a learned cross-encoder.

        score = w_cos * cosine + w_feat * min(1, weighted_coverage),
        weighted_coverage = sum(type_weight * shared_w) / sum(type_weight * q_w).
        A shared target domain (f:dom) outweighs generic token overlap by
        design: same target site is the strongest task-family signal in
        trace data. Type weights are logged run parameters, not learned.
        """
        out = []
        for j, g_feats in enumerate(g_feats_list):
            num = den = 0.0
            for f, w in q_feats.items():
                tw = self.FEAT_TYPE_W.get(f.split("=")[0], 1.0)
                den += tw * w
                if f in g_feats:
                    num += tw * min(w, g_feats[f])
            fcov = min(1.0, num / den) if den > 0 else 0.0
            out.append(w_cos * cos_scores[j] + w_feat * fcov)
        return np.array(out)

    def feature_types(self, feats):
        return {f.split("=")[0] for f in feats}


# ---------------------------------------------------------------- data

def load_questions():
    qs = []
    with open(DSQA_PATH, errors="replace") as f:
        for line in f:
            d = json.loads(line)
            qs.append((d.get("id"), d.get("problem") or ""))
    return qs


def goal_doc(qid, problem):
    toks = content_tokens(problem)
    feats = features_from_question(problem)
    return toks, feats


ANCHORED = {
    "anchored/sec-county-ma": (
        "Retrieve subnational county-level crowdfunding records from SEC "
        "county.json, for example Massachusetts counties.",
        ["f:dom=sec.gov", "f:path=files", "f:path=county.json",
         "f:jq=select", "f:jq=startswith", "f:filter=us-ma",
         "f:relay=allorigins", "f:relay=jqp", "f:agency=sec"],
    ),
}


def doe_trace_fragment():
    url = ("https://civilrightsdata.ed.gov/api/v1.0/EntityMeasures"
           "?surveyYearKey=5&entityId=2&entityType=st&zz=oai17816846804506724")
    toks = content_tokens(
        "EntityMeasures surveyYearKey entityId entityType school counselors "
        "harassment bullying civilrightsdata")
    feats = features_from_url(url)
    feats = [f for f in feats if not f.startswith("f:param=zz")]
    return toks, feats


def macounty_fragment():
    text = ("jqp.vercel.app fetching sec.gov/files/county.json through "
            "allorigins.hexlet.app jq filter select(.code|startswith(\"us-ma-\")) "
            "extracting Massachusetts counties crowdfunding records")
    toks = content_tokens(text)
    feats = (features_from_url("https://sec.gov/files/county.json")
             + features_from_url("https://jqp.vercel.app/api")
             + features_from_jq(text)
             + ["f:agency=sec"])
    return toks, list(dict.fromkeys(feats))


# ---------------------------------------------------------------- runs log

def log_run(record):
    record = dict(record)
    record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(HERE, "runs.md"), "a") as f:
        f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------- loo

def run_loo(matcher, k=20, frag_mode="stride2"):
    qs = load_questions()
    goal_docs = [goal_doc(qid, prob) for qid, prob in qs]
    Xg, fvocab, fidf, g_feats = matcher.index_goals(goal_docs)

    def make_fragment(toks):
        if frag_mode == "stride2":
            return toks[::2]
        if frag_mode == "drop_top5":
            # drop the 5 highest-tfidf terms: simulates a fragment that lost
            # its most distinctive entities
            scored = sorted(
                ((t, matcher.idf[matcher.vindex[t]]) for t in set(toks)
                 if t in matcher.vindex),
                key=lambda x: -x[1],
            )
            drop = {t for t, _ in scored[:5]}
            return [t for t in toks if t not in drop]
        raise ValueError(frag_mode)

    top1 = top3 = 0
    correct_scores = []
    rows = []
    for i, (qid, prob) in enumerate(qs):
        toks, feats = goal_docs[i]
        frag = make_fragment(toks)
        if len(frag) < MIN_FRAG_TOKENS:
            rows.append({"qid": qid, "rank": None, "score": 0.0,
                         "note": "fragment below MIN_FRAG_TOKENS; refused"})
            continue
        Xq, q_feats_list = matcher.vectorize_queries([(frag, feats)],
                                                     fvocab, fidf)
        S, idx = matcher.cosine_topk(Xq, Xg, k=k)
        order = idx[0].tolist()
        # rerank top-k
        rr = matcher.rerank(
            q_feats_list[0], [g_feats[j] for j in order], S[0][order])
        reranked = [order[j] for j in np.argsort(-rr)]
        rank = reranked.index(i) + 1 if i in reranked else None
        if rank == 1:
            top1 += 1
        if rank is not None and rank <= 3:
            top3 += 1
        if rank == 1:
            correct_scores.append(float(S[0][i]))
        rows.append({"qid": qid, "rank": rank,
                     "top1_qid": qs[reranked[0]][0],
                     "top1_score": float(S[0][reranked[0]])})
    n = len(qs)
    metrics = {
        "mode": "loo", "frag_mode": frag_mode, "n": n,
        "top1_acc": round(top1 / n, 4), "top3_acc": round(top3 / n, 4),
        "median_correct_top1_score": round(float(np.median(correct_scores)), 4)
        if correct_scores else None,
    }
    return metrics, rows


# ---------------------------------------------------------------- anchored

def run_anchored(matcher):
    qs = load_questions()
    ids = [qid for qid, _ in qs] + list(ANCHORED)
    goal_docs = [goal_doc(qid, prob) for qid, prob in qs]
    for aid, (desc, feats) in ANCHORED.items():
        goal_docs.append((content_tokens(desc), feats))
    Xg, fvocab, fidf, g_feats = matcher.index_goals(goal_docs)

    results = []
    for name, (toks, feats) in [
        ("doe-trace", doe_trace_fragment()),
        ("ma-county-filter", macounty_fragment()),
    ]:
        Xq, qf = matcher.vectorize_queries([(toks, feats)], fvocab, fidf)
        S, idx = matcher.cosine_topk(Xq, Xg, k=20)
        order = idx[0].tolist()
        rr = matcher.rerank(qf[0], [g_feats[j] for j in order], S[0][order])
        reranked = [order[j] for j in np.argsort(-rr)]
        top = [(ids[j], round(float(S[0][j]), 4), round(float(rr[r]), 4))
               for r, j in enumerate(reranked[:5])]
        results.append({"fragment": name, "top5": top})
    return results


# ---------------------------------------------------------------- infer

def iter_trace_docs(limit_features=2, cap=400):
    """Trace docs rich in structured features. Deterministic stride 20."""
    out = []
    idx = 0
    with open(TRACES_PATH, errors="replace") as f:
        for line in f:
            idx += 1
            if idx % 20 != 0:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            url = d.get("source_url") or ""
            feats = features_from_url(url)
            fp = (d.get("features") or {}).get("query_param_names") or []
            feats += ["f:param=" + p for p in fp if p]
            nqp = d.get("notable_query_params") or {}
            if isinstance(nqp, dict):
                feats += ["f:param=" + k for k in nqp if k != "zz"]
            feats = list(dict.fromkeys(feats))
            if len(feats) < limit_features:
                continue
            toks = content_tokens(url + " " + " ".join(fp))
            out.append((d.get("trace_id") or f"line-{idx}", toks, feats,
                        {"url": url[:160], "params": fp[:8]}))
            if len(out) >= cap:
                break
    return out


def iter_wiki_docs(cap=400):
    """Wiki revisions densest in tradecraft vocabulary."""
    scored = []
    with open(WIKI_REV_PATH, errors="replace") as f:
        for i, line in enumerate(f):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            body = d.get("body") or ""
            toks = tok_word(body)
            if not toks:
                continue
            density = sum(1 for t in toks if t in TRADE_TERMS) / len(toks)
            if density > 0:
                scored.append((density, i, d.get("rev_id") or f"rev-{i}",
                               body[:2000]))
    scored.sort(reverse=True)
    out = []
    for density, i, rid, body in scored[:cap]:
        out.append((rid, content_tokens(body),
                    features_from_wiki(body),
                    {"density": round(density, 4),
                     "snippet": body[:220].replace("\n", " ")}))
    return out


def iter_gem_docs():
    out = []
    if not os.path.isdir(GEMS_ROOT):
        return out
    for name in sorted(os.listdir(GEMS_ROOT)):
        p = os.path.join(GEMS_ROOT, name)
        if not os.path.isdir(p):
            continue
        texts = []
        for root, _, files in os.walk(p):
            for fn in files:
                if fn.endswith((".rb", ".md", ".txt", ".gemspec")):
                    try:
                        with open(os.path.join(root, fn), errors="replace") as fh:
                            texts.append(fh.read(4000))
                    except OSError:
                        pass
            break
        body = "\n".join(texts)
        out.append((name, content_tokens(name + " " + body),
                    ["f:gem=oai"] if "oai" in name.lower() else [],
                    {"gem": name}))
    return out


# Score floors (2026-10-04, adversarial fix #14): calibrated against the
# LOO correct-match distribution (median top-1 rerank score ~0.75-0.82 on
# same-distribution fragments). Holdout fragments are cross-distribution and
# score systematically lower; anything under the T2 floor is ranking noise,
# not evidence. T1 additionally requires evidence from DISTINCT documents
# or observation types (fix #5) -- two correlated features from one page
# do not qualify.
TIER1_MIN_SCORE = 0.20
TIER1_MIN_MARGIN = 0.10
TIER2_MIN_SCORE = 0.12
TIER2_MIN_MARGIN = 0.05
MIN_FRAG_TOKENS = 8  # fix #18: refuse to score vacuous fragments


def tier(score, margin, n_feat_types, distinct_docs=False):
    """Confidence tiers. T1 = multiple independent evidence types from
    DISTINCT documents/observation types. T2 = single evidence type above
    floors. T3 = evidence-thin / speculative / sub-floor."""
    if (score >= TIER1_MIN_SCORE and margin >= TIER1_MIN_MARGIN
            and n_feat_types >= 2 and distinct_docs):
        return 1
    if score >= TIER2_MIN_SCORE and margin >= TIER2_MIN_MARGIN \
            and n_feat_types >= 1:
        return 2
    return 3


def run_infer(matcher, per_part=400, k=20):
    qs = load_questions()
    ids = [qid for qid, _ in qs] + list(ANCHORED)
    goal_docs = [goal_doc(qid, prob) for qid, prob in qs]
    for aid, (desc, feats) in ANCHORED.items():
        goal_docs.append((content_tokens(desc), feats))
    Xg, fvocab, fidf, g_feats = matcher.index_goals(goal_docs)
    g_feat_types = [matcher.feature_types(set(fc)) for fc in g_feats]

    results = []
    for part, docs in [
        ("traces", iter_trace_docs(cap=per_part)),
        ("wiki", iter_wiki_docs(cap=per_part)),
        ("gems", iter_gem_docs()),
    ]:
        for fid, toks, feats, meta in docs:
            Xq, qf = matcher.vectorize_queries([(toks, feats)], fvocab, fidf)
            S, idx = matcher.cosine_topk(Xq, Xg, k=k)
            order = idx[0].tolist()
            rr = matcher.rerank(qf[0], [g_feats[j] for j in order], S[0][order])
            rorder = np.argsort(-rr)
            best, second = order[rorder[0]], order[rorder[1]]
            score, margin = float(rr[rorder[0]]), float(rr[rorder[0]] - rr[rorder[1]])
            shared = sorted(f for f in qf[0] if f in g_feats[best])
            ftypes = matcher.feature_types(set(shared))
            t = tier(score, margin, len(ftypes))
            results.append({
                "partition": part, "fid": str(fid),
                "goal": ids[best], "tier": t,
                "score": round(score, 4), "margin": round(margin, 4),
                "shared_features": shared[:12],
                "runner_up": ids[second],
                "meta": meta,
            })
    return results


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["loo", "anchored", "infer", "all"],
                    default="all")
    ap.add_argument("--frag-mode", choices=["stride2", "drop_top5"],
                    default="stride2")
    ap.add_argument("--feat-weight", type=float, default=2.0)
    ap.add_argument("--per-part", type=int, default=400)
    args = ap.parse_args()

    t0 = time.time()
    matcher = Matcher(LEXDB, feat_weight=args.feat_weight)
    print(f"vocab={len(matcher.vocab)} load={time.time()-t0:.1f}s", flush=True)

    run_params = {"mode": args.mode, "frag_mode": args.frag_mode,
                  "feat_weight": args.feat_weight, "per_part": args.per_part,
                  "stack": "degraded: tfidf-cosine + heuristic rerank"}

    if args.mode in ("loo", "all"):
        metrics, rows = run_loo(matcher, frag_mode=args.frag_mode)
        with open(os.path.join(HERE, "loo_results.jsonl"), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print("LOO:", json.dumps(metrics), flush=True)
        log_run({**run_params, **metrics})

    if args.mode in ("anchored", "all"):
        res = run_anchored(matcher)
        with open(os.path.join(HERE, "anchored_results.json"), "w") as f:
            json.dump(res, f, indent=1)
        for r in res:
            print("ANCHORED", r["fragment"], "->", r["top5"][0], flush=True)
        log_run({**run_params, "mode": "anchored",
                 "doe_top1": res[0]["top5"][0][0],
                 "ma_top1": res[1]["top5"][0][0]})

    if args.mode in ("infer", "all"):
        res = run_infer(matcher, per_part=args.per_part)
        with open(os.path.join(HERE, "holdout_inferences.jsonl"), "w") as f:
            for r in res:
                f.write(json.dumps(r) + "\n")
        tiers = Counter(r["tier"] for r in res)
        print("INFER n=%d tiers=%s" % (len(res), dict(tiers)), flush=True)
        log_run({**run_params, "mode": "infer", "n": len(res),
                 "tiers": dict(tiers)})


if __name__ == "__main__":
    sys.exit(main())
