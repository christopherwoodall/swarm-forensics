#!/usr/bin/env python3
"""Pattern database: SQLite (stdlib only). No fancy algorithms.

Tables:
  url_templates   normalized URL shapes with slots for nonces/ids
  relay_chains    ordered host sequences per request chain
  param_grammars  param-name sets per host
  nonce_templates regex shapes of zz/epoch/nonce-ish values
  action_ngrams   tool-call bigrams/trigrams from claude_code sessions and
                  chat speaker sequences (computer_use_turns when available)

Mining is plain: frequency ranks, P(next|current), P(param|host),
sequential counts. make patterns -> builds DB + PATTERNS.md.
"""
import gzip
import json
import re
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, unquote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_b import parse_request, iter_trace_urls, iter_wiki_urls, SILENT  # noqa: E402

DB = HERE / "patterns.sqlite"
DATA_RAW = HERE.parent / "stylometry" / "data" / "raw"


def value_shape(v):
    if re.fullmatch(r"oai\d+", v):
        return "{oai_tag}"
    if re.fullmatch(r"0\.\d{10,}", v):
        return "{float_nonce}"
    if re.fullmatch(r"\d{10,}", v):
        return "{epoch}"
    if re.fullmatch(r"[0-9a-f-]{16,}", v):
        return "{hexid}"
    if re.fullmatch(r"\d+", v):
        return "{int}"
    if "://" in v or "%3A%2F%2F" in v:
        return "{url}"
    if v == "":
        return "{empty}"
    if len(v) > 40:
        return "{long}"
    return "{text}"


def url_template(url):
    """scheme://host/path-template?param=shape&..."""
    u = url
    if re.search(r"https?://https?://", u):
        u = re.sub(r"https?://https?://", "http://", u, count=1)
    try:
        p = urlparse(u)
    except ValueError:
        return None
    host = (p.hostname or "").lower()
    if not host:
        return None
    segs = []
    for s in p.path.split("/"):
        if not s:
            continue
        if re.fullmatch(r"\d+", s):
            segs.append("{id}")
        elif re.fullmatch(r"[0-9a-f-]{20,}", s):
            segs.append("{hexid}")
        elif re.fullmatch(r"0\.\d{10,}", s):
            segs.append("{nonce}")
        else:
            segs.append(s.lower()[:40])
    try:
        params = parse_qsl(p.query, keep_blank_values=True)
    except ValueError:
        params = []
    q = "&".join(f"{k}={value_shape(v)}" for k, v in sorted(params))
    t = f"{p.scheme}://{host}/" + "/".join(segs)
    return t + ("?" + q if q else "")


NONCE_VAL = [
    ("zz_oai", re.compile(r"^oai\d+$")),
    ("float_nonce", re.compile(r"^0\.\d{10,}$")),
    ("epoch_ns", re.compile(r"^\d{16,}$")),
    ("epoch_s", re.compile(r"^\d{10}$")),
    ("hex16", re.compile(r"^[0-9a-f]{16,}$")),
    ("cachebust_int", re.compile(r"^\d{4,9}$")),
]


def build():
    if DB.exists():
        DB.unlink()
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE url_templates(template TEXT, host TEXT, n INT, example TEXT);
    CREATE TABLE relay_chains(chain TEXT, n INT, example TEXT);
    CREATE TABLE param_grammars(host TEXT, param_set TEXT, n INT);
    CREATE TABLE nonce_templates(shape TEXT, param TEXT, n INT, example TEXT);
    CREATE TABLE action_ngrams(source TEXT, ngram TEXT, n INT);
    CREATE INDEX idx_ut_host ON url_templates(host);
    CREATE INDEX idx_pg_host ON param_grammars(host);
    """)
    tpl = Counter()
    tpl_ex = {}
    chains = Counter()
    chain_ex = {}
    pgram = Counter()
    nonce = Counter()
    nonce_ex = {}

    def ingest(url):
        nodes, chain = parse_request(url)
        t = url_template(url)
        if t:
            try:
                host = urlparse(t).hostname or ""
            except ValueError:
                host = ""
            tpl[(t, host)] += 1
            tpl_ex.setdefault((t, host), url[:300])
        if chain:
            # full ordered chain incl. target: rebuild from parse
            hs = []
            for m in re.finditer(r"https?://", unquote(url)):
                try:
                    h = urlparse(unquote(url)[m.start():]).hostname or ""
                except ValueError:
                    continue
                h = h.lower()
                if h and h not in hs:
                    hs.append(h)
            if len(hs) > 1:
                key = " > ".join(hs)
                chains[key] += 1
                chain_ex.setdefault(key, url[:300])
        # param grammar per outermost host
        try:
            outer = (urlparse(url).hostname or "").lower()
            params = parse_qsl(urlparse(url).query, keep_blank_values=True)
        except ValueError:
            return
        if params and outer:
            pset = ",".join(sorted(k for k, _ in params))
            pgram[(outer, pset)] += 1
            for k, v in params:
                for shape, rx in NONCE_VAL:
                    if rx.match(v):
                        nonce[(shape, k)] += 1
                        nonce_ex.setdefault((shape, k), v[:60])

    n_url = 0
    for url, _ in iter_trace_urls():
        ingest(url)
        n_url += 1
    for url, _ in iter_wiki_urls():
        ingest(url)
        n_url += 1

    c.executemany("INSERT INTO url_templates VALUES (?,?,?,?)",
                  [(t, h, n, tpl_ex[(t, h)]) for (t, h), n in tpl.items()])
    c.executemany("INSERT INTO relay_chains VALUES (?,?,?)",
                  [(k, n, chain_ex[k]) for k, n in chains.items()])
    c.executemany("INSERT INTO param_grammars VALUES (?,?,?)",
                  [(h, p, n) for (h, p), n in pgram.items()])
    c.executemany("INSERT INTO nonce_templates VALUES (?,?,?,?)",
                  [(s, p, n, nonce_ex[(s, p)]) for (s, p), n in nonce.items()])

    # action n-grams: claude_code message sequences per session
    grams = Counter()
    p = DATA_RAW / "claude_code_messages.jsonl.gz"
    if p.exists():
        sess = {}
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                sid = r.get("sdk_session_id") or r.get("agent_id")
                mt = f"{r.get('message_type')}:{r.get('message_subtype')}"
                sess.setdefault(sid, []).append((r.get("created_at") or "", mt))
        for sid, seq in sess.items():
            seq = [m for _, m in sorted(seq)]
            for i in range(len(seq) - 1):
                grams[("claude", " ".join(seq[i:i + 2]))] += 1
            for i in range(len(seq) - 2):
                grams[("claude", " ".join(seq[i:i + 3]))] += 1
    # chat speaker sequences per room
    p = DATA_RAW / "chat_messages.jsonl.gz"
    if p.exists():
        rooms = {}
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                rooms.setdefault(r.get("room_id"), []).append(
                    (r.get("created_at") or "", r.get("speaker_type")))
        for rid, seq in rooms.items():
            seq = [s for _, s in sorted(seq)]
            for i in range(len(seq) - 1):
                grams[("chat", " ".join(seq[i:i + 2]))] += 1
            for i in range(len(seq) - 2):
                grams[("chat", " ".join(seq[i:i + 3]))] += 1
    # computer_use_turns agent_action sequences per session (all 5 tables in)
    p = DATA_RAW / "computer_use_turns.jsonl.gz"
    if p.exists():
        from collections import defaultdict as _dd
        sess = _dd(list)
        try:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                for line in f:
                    r = json.loads(line)
                    a = r.get("agent_action")
                    lab = None
                    if isinstance(a, dict) and isinstance(a.get("command"), str):
                        first = a["command"].strip().split("\n")[0].lstrip("# ").strip()
                        lab = "sh:" + (first.split()[0] if first.split() else "empty")
                    elif a:
                        lab = str(a)[:40]
                    if lab:
                        sess[r.get("session_id")].append(
                            (r.get("created_at") or "", lab))
        except EOFError:
            print("WARN truncated turns gzip tolerated", flush=True)
        for sid, seq in sess.items():
            seq = [l for _, l in sorted(seq)]
            for i in range(len(seq) - 1):
                grams[("turns", " ".join(seq[i:i + 2]))] += 1
            for i in range(len(seq) - 2):
                grams[("turns", " ".join(seq[i:i + 3]))] += 1
    c.executemany("INSERT INTO action_ngrams VALUES (?,?,?)",
                  [(s, g, n) for (s, g), n in grams.items()])
    c.commit()

    # ---- mining ----
    md = ["# Pattern database findings", ""]
    md.append(f"Built {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
              f"from {n_url} URLs + village sessions.")
    md.append("")
    md.append("## url_templates (top 20)")
    for t, h, n, _ in c.execute(
            "SELECT template,host,n,example FROM url_templates ORDER BY n DESC LIMIT 20"):
        md.append(f"- {n}x `{t[:150]}`")
    md.append("")
    md.append("## relay_chains (top 20)")
    for k, n, _ in c.execute(
            "SELECT chain,n,example FROM relay_chains ORDER BY n DESC LIMIT 20"):
        md.append(f"- {n}x {k}")
    md.append("")
    md.append("## P(next hop | current hop) (top 15, min 5)")
    trans = Counter()
    cur = Counter()
    for k, n in c.execute("SELECT chain,n FROM relay_chains"):
        hs = k.split(" > ")
        for a, b in zip(hs, hs[1:]):
            trans[(a, b)] += n
            cur[a] += n
    for (a, b), n in trans.most_common(60):
        if n >= 5:
            md.append(f"- P({b} | {a}) = {n/cur[a]:.2f} ({n}/{cur[a]})")
            if len([l for l in md if l.startswith("- P(")]) >= 15:
                break
    md.append("")
    md.append("## param_grammars: P(param | host) for top hosts")
    for (h,), in c.execute(
            "SELECT host FROM param_grammars GROUP BY host ORDER BY SUM(n) DESC LIMIT 8"):
        tot = c.execute("SELECT SUM(n) FROM param_grammars WHERE host=?", (h,)).fetchone()[0]
        pc = Counter()
        for ps, n in c.execute("SELECT param_set,n FROM param_grammars WHERE host=?", (h,)):
            for p_ in ps.split(","):
                pc[p_] += n
        top = ", ".join(f"{p_} {pc[p_]/tot:.2f}" for p_, _ in pc.most_common(6))
        md.append(f"- {h} ({tot}): {top}")
    md.append("")
    md.append("## nonce_templates")
    for s, p_, n, ex in c.execute(
            "SELECT shape,param,n,example FROM nonce_templates ORDER BY n DESC"):
        md.append(f"- {n}x {s} in `{p_}` e.g. `{ex[:50]}`")
    md.append("")
    md.append("## action_ngrams (top 15 per source)")
    for (s,), in c.execute("SELECT DISTINCT source FROM action_ngrams"):
        md.append(f"### {s}")
        for g, n in c.execute(
                "SELECT ngram,n FROM action_ngrams WHERE source=? ORDER BY n DESC LIMIT 15", (s,)):
            md.append(f"- {n}x {g}")
    md.append("")
    (HERE / "PATTERNS.md").write_text("\n".join(md))
    print("\n".join(md[:40]), flush=True)
    print(f"... full report -> PATTERNS.md; db={DB}", flush=True)


if __name__ == "__main__":
    sys.exit(build())
