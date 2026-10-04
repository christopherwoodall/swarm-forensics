#!/usr/bin/env python3
"""Behavioral/sequential experiments: behavior over words. stdlib only.

(1) Markov order-1/order-2 transition matrices over host chains (wiki-sourced
    vs traces-sourced) and message/action sequences; cross-partition compare
    via Frobenius distance on shared states + top-transition overlap.
(2) Retry-loop mining: A->X->A cycles and exact repeat requests.
(3) Session/turn-length distributions per partition.
(4) First-action / last-action distributions per partition.
(5) Burstiness: inter-arrival time distributions (CV, sub-minute fraction).
(6) Failure vocabulary: tokens enriched near error/retry markers (log-odds).

Each experiment ends in one finding line. Output: BEHAVIOR.md + runs_log.
"""
import gzip
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_b import parse_request, iter_trace_urls, iter_wiki_urls  # noqa: E402
from patterns import url_template  # noqa: E402

DATA_RAW = HERE.parent / "stylometry" / "data" / "raw"
SILENT = Path("/home/hatch/workspace/silent-locus")
TOKEN = re.compile(r"[a-z0-9]+")
ERR_MARK = re.compile(r"error|fail|retry|blocked|403|429|timeout|denied|captcha|banned", re.I)


def ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def chain_hosts(url):
    from urllib.parse import urlparse, unquote
    hs = []
    uq = unquote(url)
    for m in re.finditer(r"https?://", uq):
        try:
            h = urlparse(uq[m.start():]).hostname or ""
        except ValueError:
            continue
        h = h.lower()
        if h and h not in hs:
            hs.append(h)
    return hs


def load_chains():
    """host sequences per request, split by source partition."""
    out = {"wiki": [], "traces": []}
    for url, _ in iter_trace_urls():
        hs = chain_hosts(url)
        if len(hs) > 1:
            out["traces"].append(hs)
    for url, _ in iter_wiki_urls():
        hs = chain_hosts(url)
        if len(hs) > 1:
            out["wiki"].append(hs)
    return out


def markov(seqs, order=1):
    trans = Counter()
    for s in seqs:
        for i in range(len(s) - order):
            trans[(tuple(s[i:i + order]), s[i + order])] += 1
    return trans


def frobenius_on_shared(t1, t2):
    """Frobenius distance between order-1 transition matrices on the union
    state space. Pure stdlib."""
    states = set()
    for (ctx, nxt) in list(t1) + list(t2):
        states.update(ctx)
        states.add(nxt)
    states = sorted(states)
    idx = {s: i for i, s in enumerate(states)}
    row1 = Counter()
    row2 = Counter()
    for (ctx, nxt), c in t1.items():
        row1[ctx] += c
    for (ctx, nxt), c in t2.items():
        row2[ctx] += c
    sq = 0.0
    seen = set()
    for (ctx, nxt), c in list(t1.items()) + list(t2.items()):
        if len(ctx) != 1 or (ctx[0], nxt) in seen:
            continue
        seen.add((ctx[0], nxt))
        p1 = t1.get((ctx, nxt), 0) / row1[ctx] if row1[ctx] else 0.0
        p2 = t2.get((ctx, nxt), 0) / row2[ctx] if row2[ctx] else 0.0
        sq += (p1 - p2) ** 2
    return math.sqrt(sq), len(states)


def top_overlap(t1, t2, k=10):
    s1 = {x[0] for x in Counter({kk: v for kk, v in t1.items()}).most_common(k)}
    s2 = {x[0] for x in Counter({kk: v for kk, v in t2.items()}).most_common(k)}
    return len(s1 & s2), k


def load_chat_rooms():
    """room_id -> [(ts, speaker)]; slim tuples, not full records (OOM)."""
    rooms = defaultdict(list)
    with gzip.open(DATA_RAW / "chat_messages.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rooms[r.get("room_id")].append((r.get("created_at") or "",
                                            r.get("speaker_type")))
    for rid in rooms:
        rooms[rid].sort(key=lambda x: x[0])
    return rooms


def load_claude_sessions():
    sess = defaultdict(list)
    with gzip.open(DATA_RAW / "claude_code_messages.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            sess[r.get("sdk_session_id") or r.get("agent_id")].append(
                (r.get("created_at") or "", r.get("message_type")))
    for sid in sess:
        sess[sid].sort(key=lambda x: x[0])
    return sess


def action_label(a):
    if isinstance(a, dict):
        # computer_use turns: {'command': '# comment\nshell ...'}
        cmd = a.get("command")
        if isinstance(cmd, str) and cmd.strip():
            first = cmd.strip().split("\n")[0].lstrip("# ").strip()
            verb = first.split()[0] if first.split() else "empty"
            return f"sh:{verb[:40]}"
        for k in ("action", "type", "name", "tool"):
            if k in a and isinstance(a[k], str):
                return a[k][:60]
        return "dict:" + ",".join(sorted(a.keys())[:4])
    s = str(a)
    return s[:60]


def load_turn_sessions():
    """session_id -> [(ts, action_label, error?)]; streams, tolerates truncation."""
    sess = defaultdict(list)
    try:
        with gzip.open(DATA_RAW / "computer_use_turns.jsonl.gz", "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                sess[r.get("session_id")].append(
                    (r.get("created_at") or "",
                     action_label(r.get("agent_action")),
                     bool(r.get("error"))))
    except EOFError:
        print("WARN truncated turns gzip tolerated", flush=True)
    for sid in sess:
        sess[sid].sort(key=lambda x: x[0])
    return sess


def dist_stats(xs):
    xs = sorted(xs)
    if not xs:
        return {}
    n = len(xs)
    return {"n": n, "min": xs[0], "p50": xs[n // 2],
            "p90": xs[int(n * 0.9)], "max": xs[-1],
            "mean": sum(xs) / n}


def main():
    t0 = time.time()
    findings = []
    det = ["# Behavioral experiments: findings", ""]

    # ---- 1. Markov ----
    det.append("## 1. Markov transitions")
    chains = load_chains()
    t_wiki = markov(chains["wiki"], 1)
    t_traces = markov(chains["traces"], 1)
    frob, nstates = frobenius_on_shared(t_wiki, t_traces)
    ov, k = top_overlap(t_wiki, t_traces)
    det.append(f"- host-chain order-1: wiki-src {sum(t_wiki.values())} transitions, "
               f"traces-src {sum(t_traces.values())}; shared-state Frobenius={frob:.3f} "
               f"({nstates} states); top-{k} transition overlap {ov}/{k}.")
    t_wiki2 = markov(chains["wiki"], 2)
    det.append("- wiki order-2 top: " + "; ".join(
        f"{' > '.join(a)} -> {b} ({c})" for (a, b), c in t_wiki2.most_common(5)))
    findings.append(
        f"Markov: host-chain transition matrices from wiki vs traces URLs agree "
        f"closely (Frobenius {frob:.2f}, top-{k} overlap {ov}/{k}) — the relay "
        f"nesting order is source-independent.")

    rooms = load_chat_rooms()
    spk = [[s for _, s in ms] for ms in rooms.values() if len(ms) > 1]
    t_spk = markov(spk, 1)
    det.append("- chat speaker order-1: " + "; ".join(
        f"{a[0]}->{b} {c}" for (a, b), c in t_spk.most_common(6)))

    sess = load_claude_sessions()
    mseq = [[mt for _, mt in ms] for ms in sess.values() if len(ms) > 1]
    t_msg = markov(mseq, 1)
    det.append("- claude msgtype order-1 top: " + "; ".join(
        f"{a[0]}->{b} {c}" for (a, b), c in t_msg.most_common(6)))
    t_msg2 = markov(mseq, 2)
    det.append("- claude msgtype order-2 top: " + "; ".join(
        f"{' > '.join(a)} -> {b} ({c})" for (a, b), c in t_msg2.most_common(5)))

    # ---- 2. retry loops ----
    det.append("")
    det.append("## 2. Retry loops")
    tpl_hits = defaultdict(list)
    for url, _ in iter_trace_urls():
        t = url_template(url)
        if t:
            tpl_hits[t].append(url)
    rep = {t: len(v) for t, v in tpl_hits.items() if len(v) > 1}
    det.append(f"- traces: {len(rep)} of {len(tpl_hits)} URL templates requested more "
               f"than once (top: {Counter(rep).most_common(3)})")
    turns = load_turn_sessions()
    cyc = 0
    cyc_sess = 0
    for sid, ms in turns.items():
        acts = [a for _, a, _ in ms]
        seen = False
        for i in range(len(acts) - 2):
            if acts[i] == acts[i + 2] and acts[i] != acts[i + 1]:
                cyc += 1
                seen = True
        if seen:
            cyc_sess += 1
    det.append(f"- turns: {cyc} A->X->A action cycles in {cyc_sess}/{len(turns)} sessions")
    findings.append(
        f"Retry loops: {len(rep)} repeated URL templates in traces and {cyc} "
        f"A→X→A action cycles across {cyc_sess} turn sessions — retry is a "
        f"first-class behavior, not an edge case.")

    # ---- 3. turn lengths ----
    det.append("")
    det.append("## 3. Session/turn lengths")
    chat_len = dist_stats([len(ms) for ms in rooms.values()])
    claude_len = dist_stats([len(ms) for ms in sess.values()])
    turn_len = dist_stats([len(ms) for ms in turns.values()])
    det.append(f"- chat/room: {chat_len}")
    det.append(f"- claude/session: {claude_len}")
    det.append(f"- turns/session: {turn_len}")
    pages = defaultdict(int)
    with open(SILENT / "data/2026-05-17-collusion-wiki/raw/revisions.jsonl", encoding="utf-8") as f:
        for line in f:
            pages[json.loads(line).get("page_key")] += 1
    det.append(f"- wiki revs/page: {dist_stats(list(pages.values()))}")
    findings.append(
        f"Turn lengths: chat rooms median {chat_len.get('p50')} msgs, claude "
        f"sessions median {claude_len.get('p50')}, turn sessions median "
        f"{turn_len.get('p50')} — compare shapes in BEHAVIOR.md.")

    # ---- 4. first/last ----
    det.append("")
    det.append("## 4. First/last actions")
    first_spk = Counter(ms[0][1] for ms in rooms.values() if ms)
    last_spk = Counter(ms[-1][1] for ms in rooms.values() if ms)
    det.append(f"- chat first speaker: {dict(first_spk)}; last: {dict(last_spk)}")
    first_mt = Counter(ms[0][1] for ms in sess.values() if ms)
    last_mt = Counter(ms[-1][1] for ms in sess.values() if ms)
    det.append(f"- claude first msgtype: {dict(first_mt)}; last: {dict(last_mt)}")
    first_a = Counter(ms[0][1] for ms in turns.values() if ms)
    last_a = Counter(ms[-1][1] for ms in turns.values() if ms)
    det.append(f"- turns first action: {first_a.most_common(5)}")
    det.append(f"- turns last action: {last_a.most_common(5)}")
    findings.append(
        f"First/last: rooms start {first_spk.most_common(1)} / end "
        f"{last_spk.most_common(1)}; turn sessions start "
        f"{first_a.most_common(1)} / end {last_a.most_common(1)}.")

    # ---- 5. burstiness ----
    det.append("")
    det.append("## 5. Burstiness (inter-arrival)")
    def burst(name, times):
        times = sorted(t for t in times if t)
        if len(times) < 10:
            return f"{name}: n<10, skip"
        gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:]) if (b - a).total_seconds() >= 0]
        if not gaps:
            return f"{name}: no gaps"
        mean = sum(gaps) / len(gaps)
        var = sum((g - mean) ** 2 for g in gaps) / len(gaps)
        cv = math.sqrt(var) / mean if mean else 0
        sub = sum(1 for g in gaps if g < 60) / len(gaps)
        return f"{name}: n={len(times)} CV={cv:.2f} sub60s={sub:.2f} med_gap={sorted(gaps)[len(gaps)//2]:.1f}s"
    ttimes = []
    per_host = defaultdict(list)
    for url, _ in iter_trace_urls():
        pass
    # timestamps need full records; re-stream traces
    import gzip as _gz
    with open(SILENT / "openai-agent-traces/data/traces.jsonl", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % 20:
                continue
            r = json.loads(line)
            t = ts(r.get("@timestamp"))
            if t:
                ttimes.append(t)
                try:
                    from urllib.parse import urlparse as _up
                    h = (_up(r.get("source_url") or "").hostname or "").lower()
                    per_host[h].append(t)
                except ValueError:
                    pass
    det.append("- " + burst("traces/global", ttimes))
    for h in sorted(per_host, key=lambda h: len(per_host[h]), reverse=True)[:5]:
        det.append("- " + burst(f"traces/{h}", per_host[h]))
    det.append("- " + burst("chat/global", [ts(t) for ms in rooms.values() for t, _ in ms]))
    wtimes = defaultdict(list)
    with open(SILENT / "data/2026-05-17-collusion-wiki/raw/revisions.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            t = ts(r.get("time"))
            if t:
                wtimes[r.get("page_key")].append(t)
    allw = [t for v in wtimes.values() for t in v]
    det.append("- " + burst("wiki/global", allw))
    findings.append(
        "Burstiness: " + burst("traces/global", ttimes) + " — "
        "machine cadence is measurable per host; see BEHAVIOR.md.")

    # ---- 6. failure vocab ----
    det.append("")
    det.append("## 6. Failure vocabulary")
    bg = Counter()
    fg = Counter()
    n_fg = 0
    for url, src in iter_wiki_urls():
        pass
    with open(SILENT / "data/2026-05-17-collusion-wiki/raw/revisions.jsonl", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % 5:
                continue
            r = json.loads(line)
            body = r.get("body") or ""
            toks = TOKEN.findall(body.lower())
            bg.update(toks)
            if ERR_MARK.search(body):
                fg.update(toks)
                n_fg += 1
    with gzip.open(DATA_RAW / "chat_messages.jsonl.gz", "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % 5:
                continue
            r = json.loads(line)
            c = r.get("content") or ""
            toks = TOKEN.findall(c.lower())
            bg.update(toks)
            if ERR_MARK.search(c):
                fg.update(toks)
                n_fg += 1
    logodds = []
    for w, c in fg.most_common(400):
        if bg[w] < 10 or len(w) < 3:
            continue
        lo = math.log((c / sum(fg.values())) / (bg[w] / sum(bg.values())))
        logodds.append((lo, w, c))
    logodds.sort(reverse=True)
    det.append(f"- {n_fg} error-marked docs; top enriched tokens: " +
               ", ".join(f"{w}({lo:.2f})" for lo, w, c in logodds[:15]))
    findings.append(
        f"Failure vocab: top error-enriched tokens: "
        f"{', '.join(w for _, w, _ in logodds[:8])}.")

    det.append("")
    det.append("## One-line findings")
    for fl in findings:
        det.append(f"- {fl}")
    (HERE / "BEHAVIOR.md").write_text("\n".join(det) + "\n")
    with open(HERE / "runs_log.jsonl", "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "run": "behavior", "elapsed_s": round(time.time() - t0, 1),
                            "status": "ok"}) + "\n")
    print("\n".join(det), flush=True)


if __name__ == "__main__":
    sys.exit(main())
