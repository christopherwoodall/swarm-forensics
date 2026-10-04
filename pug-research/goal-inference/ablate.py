#!/usr/bin/env python3
"""Ablations & diagnostics for the goal-inference lane. Stdlib only.

Covers (user-requested, 2026-10-04):
  (1) feature-family ablation on the matcher: lexical-only vs structured-only
      vs hybrid (top-1/top-3 per setting on the LOO eval set)
  (2) per-feature-family importance: leave-one-family-out, overall and for
      dsqa_250
  (3) village cross-task confusion matrix on labeled village tasks
  (4) prompt-element ablation: which prompt component predicts observed
      behavior best (from prompt_map.json)
  (5) evidence-type breakdown on holdout prompt inferences

Writes ablations.json next to this script and appends to runs.md.
One-line findings are copied into REPORT.md / PROMPT_INVERSION.md by hand.
"""

import gzip
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
RAW = os.path.join(REPO, "pug-research", "stylometry", "data", "raw")
SILENT = "/home/hatch/workspace/silent-locus"
DSQA = os.path.join(SILENT, "data/2026-10-01-deepsearchqa/questions.jsonl")

WORD_RE = re.compile(r"[a-z0-9]+")
DOM_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:gov|org|com|edu|net|io|au|uk|dev|app)\b")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
STOPWORDS = set(
    "the a an and or of to in is are was were be been being for on at as by "
    "with from that this it its it’s which who whom whose what when where how "
    "why not no yes do does did done have has had having will would can could "
    "should shall may might must than then there here than too very into over "
    "under between through during each other more most some any all both own "
    "same per via within without about against among".split())

FAMILIES = ["dom", "param", "path", "jq", "filter", "relay", "agency", "year"]


def toks(text):
    return [t for t in WORD_RE.findall(text.lower()) if t not in STOPWORDS]


def feats_of(text):
    low = text.lower()
    f = []
    for d in set(DOM_RE.findall(low)):
        f.append("f:dom=" + (d[4:] if d.startswith("www.") else d))
    for m in YEAR_RE.finditer(low):
        f.append("f:year=" + m.group(0))
    words = set(WORD_RE.findall(low))
    for ag in ("sec", "doe", "bea", "cdc", "fbi", "doj", "census", "aihw",
               "unctad", "ihme"):
        if ag in words:
            f.append("f:agency=" + ag)
    return f


def fam_of(feat):
    return feat.split("=")[0][2:] if feat.startswith("f:") else "word"


class Tfidf:
    def __init__(self):
        self.df = Counter()
        self.n = 0
        self.idf = {}

    def add_doc(self, terms):
        self.n += 1
        for t in set(terms):
            self.df[t] += 1

    def finalize(self):
        self.idf = {t: math.log(1 + self.n / (1 + c))
                    for t, c in self.df.items()}

    def vec(self, terms):
        tf = Counter(terms)
        v, norm = {}, 0.0
        for t, c in tf.items():
            if t in self.idf:
                w = (1 + math.log(c)) * self.idf[t]
                v[t] = w
                norm += w * w
        norm = math.sqrt(norm) or 1.0
        return {t: w / norm for t, w in v.items()}


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(w * b[t] for t, w in a.items() if t in b)


def load_questions():
    qs = []
    with open(DSQA, errors="replace") as f:
        for line in f:
            d = json.loads(line)
            qs.append((d.get("id"), d.get("problem") or ""))
    return qs


def degrade(tok_list, idf, mode):
    if mode == "stride2":
        return tok_list[::2]
    if mode == "drop_top5":
        scored = sorted(((t, idf.get(t, 0.0)) for t in set(tok_list)),
                         key=lambda x: -x[1])
        drop = {t for t, _ in scored[:5]}
        return [t for t in tok_list if t not in drop]
    raise ValueError(mode)


def build_index(qs, feat_subset=None, lex=True, struct=True, fw=2.0):
    """feat_subset: None = all families; else keep only these families."""
    docs = []
    for qid, prob in qs:
        wt = toks(prob) if lex else []
        ft = feats_of(prob) if struct else []
        if feat_subset is not None:
            ft = [x for x in ft if fam_of(x) in feat_subset]
        # feat_weight stand-in: repeat structured tokens fw times
        docs.append((qid, wt + ft * int(fw)))
    tfidf = Tfidf()
    for _, terms in docs:
        tfidf.add_doc(terms)
    tfidf.finalize()
    vecs = [(qid, tfidf.vec(terms)) for qid, terms in docs]
    return tfidf, vecs


def qterms(prob, idf, frag_mode, lex=True, struct=True, feat_subset=None, fw=2.0):
    wt = toks(prob) if lex else []
    frag = degrade(wt, idf, frag_mode)
    ft = feats_of(prob) if struct else []
    if feat_subset is not None:
        ft = [x for x in ft if fam_of(x) in feat_subset]
    return frag + ft * int(fw)


def loo_accuracy(qs, tfidf, vecs, frag_mode, lex=True, struct=True,
                 feat_subset=None, fw=2.0):
    top1 = top3 = 0
    ranks = []
    for i, (qid, prob) in enumerate(qs):
        terms = qterms(prob, tfidf.idf, frag_mode, lex, struct, feat_subset, fw)
        if len(terms) < 8:  # MIN_FRAG_TOKENS guard
            ranks.append(None)
            continue
        qv = tfidf.vec(terms)
        scored = sorted(((cosine(qv, v), j) for j, (_, v) in enumerate(vecs)),
                        key=lambda x: -x[0])
        order = [j for _, j in scored[:20]]
        rank = order.index(i) + 1 if i in order else None
        ranks.append(rank)
        if rank == 1:
            top1 += 1
        if rank is not None and rank <= 3:
            top3 += 1
    n = len([r for r in ranks if r is not None])
    return top1 / len(qs), top3 / len(qs), ranks


# ---------------------------------------------------------------- (1) family ablation

def ablation_families(qs):
    out = {}
    for name, kw in [("lexical_only", dict(lex=True, struct=False)),
                     ("structured_only", dict(lex=False, struct=True)),
                     ("hybrid", dict(lex=True, struct=True))]:
        for fm in ("stride2", "drop_top5"):
            tfidf, vecs = build_index(qs, **kw)
            t1, t3, _ = loo_accuracy(qs, tfidf, vecs, fm, **kw)
            out[f"{name}/{fm}"] = {"top1": round(t1, 4), "top3": round(t3, 4)}
            print(f"abl1 {name}/{fm}: top1={t1:.4f} top3={t3:.4f}", flush=True)
    return out


# ---------------------------------------------------------------- (2) per-family importance

def family_importance(qs):
    tfidf, vecs = build_index(qs)
    base_t1, _, base_ranks = loo_accuracy(qs, tfidf, vecs, "stride2")
    res = {"baseline_top1": round(base_t1, 4), "drop": {}}
    for fam in FAMILIES:
        keep = [f for f in FAMILIES if f != fam]
        tf2, v2 = build_index(qs, feat_subset=keep)
        t1, _, _ = loo_accuracy(qs, tf2, v2, "stride2", feat_subset=keep)
        res["drop"][fam] = round(base_t1 - t1, 4)
        print(f"abl2 drop {fam}: {base_t1 - t1:+.4f}", flush=True)
    # dsqa_250 rank sensitivity
    idx250 = next(i for i, (qid, _) in enumerate(qs) if qid == "dsqa_250")
    sens = {}
    for fam in FAMILIES:
        keep = [f for f in FAMILIES if f != fam]
        tf2, v2 = build_index(qs, feat_subset=keep)
        qid, prob = qs[idx250]
        terms = qterms(prob, tf2.idf, "stride2", feat_subset=keep)
        qv = tf2.vec(terms)
        scored = sorted(((cosine(qv, v), j) for j, (_, v) in enumerate(v2)),
                        key=lambda x: -x[0])
        order = [j for _, j in scored[:20]]
        sens[fam] = order.index(idx250) + 1 if idx250 in order else None
    res["dsqa_250_rank_without_family"] = sens
    return res


# ---------------------------------------------------------------- (3) village confusion

def village_confusion():
    goals = {}
    with gzip.open(os.path.join(RAW, "agent_goals.jsonl.gz"), "rt",
                   errors="replace") as f:
        for line in f:
            r = json.loads(line)
            if r.get("agent_id"):
                goals[r["agent_id"]] = r.get("short_name") or r.get("name")
    labels = sorted(set(goals.values()))
    print(f"abl3: {len(goals)} agents mapped to {len(labels)} goals", flush=True)
    # sample chat fragments per agent (cap for runtime)
    frags = defaultdict(list)
    n = 0
    with gzip.open(os.path.join(RAW, "chat_messages.jsonl.gz"), "rt",
                   errors="replace") as f:
        for line in f:
            if n % 5:
                n += 1
                continue
            n += 1
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("speaker_type") != "agent":
                continue
            aid = r.get("agent_speaker_id")
            if aid in goals and len(frags[aid]) < 40:
                c = (r.get("content") or "").strip()
                if len(c) >= 40:
                    frags[aid].append(c[:600])
    agents = [a for a in frags if len(frags[a]) >= 5]
    print(f"abl3: {len(agents)} agents with >=5 fragments", flush=True)
    # index: one pseudo-doc per (agent) labeled by goal; leave-one-agent-out
    docs = [(a, goals[a], toks(" ".join(frags[a]))) for a in agents]
    tfidf = Tfidf()
    for _, _, t in docs:
        tfidf.add_doc(t)
    tfidf.finalize()
    vecs = {a: tfidf.vec(t) for a, _, t in docs}
    conf = Counter()
    for a in agents:
        # query = agent's fragments; candidates = other agents
        qv = vecs[a]
        scored = sorted(
            ((cosine(qv, vecs[b]), b) for b in agents if b != a),
            key=lambda x: -x[0])
        # majority vote of top-5 neighbors' goals
        votes = Counter(goals[b] for _, b in scored[:5])
        pred = votes.most_common(1)[0][0]
        conf[(goals[a], pred)] += 1
    acc = sum(1 for (t, p) in conf.elements() if t == p) / max(
        1, sum(conf.values()))
    return {"n_agents": len(agents), "n_goals": len(labels),
            "loao_accuracy": round(acc, 4),
            "confusion": [[t, p, c] for (t, p), c in
                          sorted(conf.items(), key=lambda x: -x[1])[:25]]}


# ---------------------------------------------------------------- (4) prompt-element ablation

def prompt_element_ablation():
    m = json.load(open(os.path.join(HERE, "prompt_map.json")))
    strength = {}
    for el, a in m["associations"].items():
        deltas = [abs(v["delta"]) for v in a["markers"].values()]
        # normalize by pooled scale: use mean abs delta (descriptive)
        strength[el] = {
            "n_with": a["n_with"],
            "mean_abs_delta": round(sum(deltas) / len(deltas), 4),
            "max_abs_delta": round(max(deltas), 4),
            "top_marker": max(a["markers"].items(),
                              key=lambda kv: abs(kv[1]["delta"]))[0],
        }
    ranked = sorted(strength.items(), key=lambda kv: -kv[1]["mean_abs_delta"])
    return {"ranked": [[el, v] for el, v in ranked]}


# ---------------------------------------------------------------- (5) evidence-type breakdown

def evidence_breakdown():
    url_pat = re.compile(r"url|domain|relay|zz=|nonce|param|api-shaped|host",
                         re.I)
    struct_pat = re.compile(r"jq|label grammar|probing-shaped|filter|feature",
                            re.I)
    counts = Counter()
    n_inf = 0
    with open(os.path.join(HERE, "prompt_inferences.jsonl"),
              encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            for inf in r["inferences"]:
                n_inf += 1
                ev = " ".join(inf["evidence"])
                cats = set()
                if url_pat.search(ev):
                    cats.add("url")
                if struct_pat.search(ev):
                    cats.add("structural")
                if not cats:
                    cats.add("prose/other")
                for c in cats:
                    counts[c] += 1
    total = sum(counts.values()) or 1
    return {"n_inferences": n_inf,
            "fractions": {k: round(v / total, 3)
                          for k, v in counts.most_common()}}


def main():
    t0 = time.time()
    qs = load_questions()
    print(f"loaded {len(qs)} questions", flush=True)
    out = {}
    out["1_family_ablation"] = ablation_families(qs)
    out["2_family_importance"] = family_importance(qs)
    try:
        out["3_village_confusion"] = village_confusion()
    except FileNotFoundError as e:
        out["3_village_confusion"] = {"error": str(e)}
    try:
        out["4_prompt_element_ablation"] = prompt_element_ablation()
    except FileNotFoundError as e:
        out["4_prompt_element_ablation"] = {"error": str(e)}
    try:
        out["5_evidence_breakdown"] = evidence_breakdown()
    except FileNotFoundError as e:
        out["5_evidence_breakdown"] = {"error": str(e)}
    with open(os.path.join(HERE, "ablations.json"), "w") as f:
        json.dump(out, f, indent=1)
    rec = {"mode": "ablate", "stack": "stdlib-only tfidf",
           "elapsed_s": round(time.time() - t0, 1),
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    open(os.path.join(HERE, "runs.md"), "a").write(json.dumps(rec) + "\n")
    print("wrote ablations.json", flush=True)


if __name__ == "__main__":
    main()
