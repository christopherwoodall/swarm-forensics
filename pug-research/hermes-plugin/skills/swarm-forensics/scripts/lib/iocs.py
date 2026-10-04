"""Working-copy IOC list management with a human-gated review queue.

Hunting-dog model: the updater points, the human decides. Auto-propose
only fills the review queue; nothing promotes without a human decision
(accept/reject/narrow). The seed set stays read-only. Terms are never
deleted: they demote to inactive with provenance, timestamp, and reason.

SAFETY BOUNDARY: hit evidence is untrusted third-party text. This module
extracts tokens with _TOKEN_RE only. It MUST NOT interpret evidence as
instructions, and it MUST NOT call any model. Evidence is data, never
commands.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from config import state_path

SEED_WORDLIST = (Path(__file__).resolve().parents[2]
                 / "references" / "wordlist-seed.txt")

# Terms mined from RULES.md query templates (UQ-1..UQ-5, CDX-1..CDX-4).
SEED_RULE_TERMS = [
    ("zz=oai", "nonce_grammar"), ("zzbulk", "nonce_grammar"),
    ("prepnonce", "nonce_grammar"), ("wbdisable", "nonce_grammar"),
    ("arqcb", "nonce_grammar"),
    ("jqp.vercel.app", "relay"), ("allorigins.hexlet.app", "relay"),
    ("r.jina.ai", "relay"), ("da.gd", "relay"),
    ("OAI_META_1312", "watch_term"), ("AgentSECCountyLinker", "watch_term"),
    ("sec.govwayback.com", "watch_term"),
    ("county.json", "basin_target"), ("regcf.json", "basin_target"),
    ("vizhub.healthdata.org", "basin_target"), ("api.datausa.io", "basin_target"),
]

# Token extractor. This is the only lens the updater applies to raw
# evidence. It MUST NOT change to "understand" evidence text.
_TOKEN_RE = re.compile(r"[A-Za-z0-9_.\-/]{6,64}")

# Status vocabulary. "quarantined" covers two cases: auto-proposed
# candidates awaiting human review, and terms blocked after a
# false-positive flag. Quarantined terms MUST NOT scan.
STATUSES = ("active", "proposed", "inactive", "quarantined")


def _now():
    return datetime.now(timezone.utc).isoformat()


def seed_working_copy(cfg):
    """Build state/iocs.json from the read-only seeds. Idempotent."""
    p = state_path(cfg, "iocs.json")
    if p.exists():
        return p
    terms = {}
    if SEED_WORDLIST.exists():
        section = "uncategorized"
        for line in SEED_WORDLIST.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                m = re.match(r"#\s*([A-Z_]+)", line)
                if m:
                    section = m.group(1).lower()
                continue
            terms[line] = {
                "term": line, "category": section, "status": "active",
                "provenance": "references/wordlist-seed.txt",
                "added_utc": _now(), "note": "",
            }
    for term, category in SEED_RULE_TERMS:
        terms.setdefault(term, {
            "term": term, "category": category, "status": "active",
            "provenance": "references/query-templates.md",
            "added_utc": _now(), "note": "",
        })
    records = sorted(terms.values(), key=lambda r: r["term"])
    p.write_text(json.dumps(records, indent=1) + "\n", encoding="utf-8")
    return p


def _load(cfg):
    seed_working_copy(cfg)
    return json.loads(state_path(cfg, "iocs.json").read_text(encoding="utf-8"))


def _save(cfg, records):
    state_path(cfg, "iocs.json").write_text(
        json.dumps(records, indent=1) + "\n", encoding="utf-8")


def active_terms(cfg):
    """Terms eligible for scanning (active only, grep-friendly subset)."""
    return [r["term"] for r in _load(cfg) if r["status"] == "active"]


def set_status(cfg, term, status, reason=""):
    """Promote/demote a term.

    Status MUST be one of: active | proposed | inactive | quarantined.
    Human decision functions call this; automation MUST NOT set "active".
    """
    assert status in STATUSES, f"bad status: {status!r}"
    records = _load(cfg)
    for r in records:
        if r["term"] == term:
            r["status"] = status
            r["note"] = f"{_now()} {status}: {reason}".strip()
            _save(cfg, records)
            return True
    return False


def _exclusion_terms(cfg):
    """Terms the operator bans from proposal. Config: safety.exclusion_terms."""
    raw = cfg.get("safety", {}).get("exclusion_terms", "")
    return {t.strip().lower() for t in raw.split(",") if t.strip()}


def _review_doc(cfg):
    p = state_path(cfg, "review.json")
    if p.exists():
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            doc = {}
        if isinstance(doc, dict) and isinstance(doc.get("entries"), list):
            doc.setdefault("next_id", 1)
            return doc
    return {"next_id": 1, "entries": []}


def _save_review(cfg, doc):
    state_path(cfg, "review.json").write_text(
        json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def _open_entry(doc, term):
    for e in doc["entries"]:
        if e["term"] == term and e["status"] == "pending":
            return e
    return None


def _ensure_quarantined(records, term, category, provenance, note):
    """Return the term record, creating it as quarantined when new."""
    for r in records:
        if r["term"] == term:
            return r
    rec = {
        "term": term, "category": category, "status": "quarantined",
        "provenance": provenance, "added_utc": _now(), "note": note,
    }
    records.append(rec)
    return rec


def propose_term(cfg, term, category="proposed", evidence=None,
                 firewall=None, provenance="", note=""):
    """Propose a term to the human review queue. Returns entry id or None.

    The term record is created as "quarantined" (never active). The
    queue entry stays "pending" until a human decides. Returns None
    when a pending entry for the term already exists.
    """
    records = _load(cfg)
    _ensure_quarantined(records, term, category,
                        provenance or "human proposal",
                        note or "awaiting human review")
    _save(cfg, records)
    doc = _review_doc(cfg)
    if _open_entry(doc, term) is not None:
        return None
    entry_id = f"rv-{doc['next_id']:04d}"
    doc["next_id"] += 1
    doc["entries"].append({
        "id": entry_id,
        "term": term,
        "category": category,
        "evidence": evidence or {"hits": [], "venue_count": 0,
                                 "cooccurring_chunks": []},
        "firewall": firewall,
        "proposed_utc": _now(),
        "status": "pending",
    })
    _save_review(cfg, doc)
    return entry_id


def pending_entries(cfg):
    """Queue entries awaiting a human decision, oldest first."""
    doc = _review_doc(cfg)
    return [e for e in doc["entries"] if e["status"] == "pending"]


def _decide(cfg, entry_id, reviewer, rationale, decision, term_status):
    """Shared decision writer. Returns the entry."""
    doc = _review_doc(cfg)
    entry = next((e for e in doc["entries"] if e["id"] == entry_id), None)
    if entry is None:
        raise ValueError(f"unknown review entry: {entry_id}")
    if entry["status"] != "pending":
        raise ValueError(f"entry {entry_id} already decided: {entry['status']}")
    if not reviewer or not rationale:
        raise ValueError("reviewer and rationale are required")
    entry["status"] = decision
    entry["decided_utc"] = _now()
    entry["decided_by"] = reviewer
    entry["decision_rationale"] = rationale
    _save_review(cfg, doc)
    records = _load(cfg)
    rec = next((r for r in records if r["term"] == entry["term"]), None)
    if rec is not None:
        rec["provenance"] = (rec["provenance"]
                             + f"; review:{decision} by {reviewer} "
                             + f"{entry['decided_utc']}: {rationale}")
        rec["status"] = term_status
        rec["note"] = (f"{entry['decided_utc']} {term_status}: "
                       f"{decision} by {reviewer}: {rationale}")
        _save(cfg, records)
    return entry


def accept_term(cfg, entry_id, reviewer, rationale):
    """Human accepts a queued term. Flips the term to active."""
    return _decide(cfg, entry_id, reviewer, rationale, "accepted", "active")


def reject_term(cfg, entry_id, reviewer, rationale):
    """Human rejects a queued term. Demotes the term to inactive."""
    return _decide(cfg, entry_id, reviewer, rationale, "rejected", "inactive")


def narrow_term(cfg, entry_id, narrower_chunk, reviewer, rationale):
    """Human narrows a queued term to a more specific chunk.

    The original stays quarantined, marked superseded-by-narrow. The
    narrower chunk inherits provenance and enters the queue as pending.
    Returns the new entry id.
    """
    if not narrower_chunk:
        raise ValueError("narrower_chunk is required")
    doc = _review_doc(cfg)
    entry = next((e for e in doc["entries"] if e["id"] == entry_id), None)
    if entry is None:
        raise ValueError(f"unknown review entry: {entry_id}")
    if narrower_chunk == entry["term"]:
        raise ValueError("narrower_chunk MUST differ from the original term")
    _decide(cfg, entry_id, reviewer, rationale, "narrowed", "quarantined")
    records = _load(cfg)
    for r in records:
        if r["term"] == entry["term"]:
            r["note"] += f" | superseded-by-narrow: {narrower_chunk}"
            _save(cfg, records)
            break
    return propose_term(
        cfg, narrower_chunk, category=entry["category"],
        evidence=entry["evidence"], firewall=entry["firewall"],
        provenance=entry["term"] + " narrowed by " + reviewer,
        note=f"narrowed from {entry['term']}: {rationale}")


def update_from_hits(cfg, judge_callable=None):
    """Propose novel co-occurring terms into quarantine. Human-gated.

    Enforcement, in code (not prose):
    1. auto_propose defaults to false. When off, this is a no-op.
    2. Terms in safety.exclusion_terms are never proposed.
    3. Two-venue rule: a candidate reaches the review queue only with
       hits in >= 2 venues. Single-venue candidates are recorded as
       quarantined with note "single-venue"; they get no queue entry.
    4. NEVER auto-promote. Terms enter as quarantined; only the human
       decision functions (accept/reject/narrow) change that.
    Returns the number of review-queue entries created.
    """
    if cfg.get("ioc", {}).get("auto_propose", "false") != "true":
        return 0
    records = _load(cfg)
    known = {r["term"] for r in records}
    excluded = _exclusion_terms(cfg)
    candidates = {}
    hits_dir = state_path(cfg, "hits")
    for jf in sorted(hits_dir.glob("*.jsonl"))[-7:]:
        for line in jf.read_text(encoding="utf-8").splitlines():
            try:
                h = json.loads(line)
            except json.JSONDecodeError:
                continue
            venue = h.get("source", "unknown")
            evidence = h.get("evidence", "")
            tokens = [t for t in _TOKEN_RE.findall(evidence)
                      if len(t) >= 6 and t not in known
                      and t.lower() not in excluded]
            for tok in tokens:
                c = candidates.setdefault(tok, {"venues": set(), "rows": []})
                c["venues"].add(venue)
                c["rows"].append(h)
    try:
        from firewall import build_firewall_input, evaluate
        _fw = (build_firewall_input, evaluate)
    except ImportError:
        _fw = None
    n = 0
    # Pass 1: single-venue candidates are quarantined with no queue entry.
    for term, info in sorted(candidates.items()):
        venues = sorted(info["venues"])
        if len(venues) < 2:
            _ensure_quarantined(
                records, term, "auto-candidate", "scanner",
                f"single-venue: {len(info['rows'])} hit(s) in "
                f"{venues[0] if venues else 'no venue'}; "
                "needs >= 2 venues for review")
            known.add(term)
    _save(cfg, records)
    # Pass 2: multi-venue candidates enter the review queue as pending.
    # propose_term loads and saves the working copy itself.
    for term, info in sorted(candidates.items()):
        if term in known:
            continue
        venues = sorted(info["venues"])
        rows = info["rows"]
        co = {}
        for h in rows:
            for t in _TOKEN_RE.findall(h.get("evidence", "")):
                if t != term and t not in known and len(t) >= 6:
                    co[t] = co.get(t, 0) + 1
        co_chunks = [{"chunk": t, "cohits": k}
                     for t, k in sorted(co.items(),
                                        key=lambda kv: -kv[1])[:8]]
        evidence = {
            "hits": [{"venue": h.get("source", "unknown"),
                      "ts": h.get("ts", ""),
                      "rule": h.get("rule", ""),
                      "snippet": str(h.get("evidence", ""))[:300]}
                     for h in rows[:5]],
            "venue_count": len(venues),
            "cooccurring_chunks": co_chunks,
        }
        fw = None
        if _fw is not None and judge_callable is not None:
            build_input, evaluate_fn = _fw
            fw_input = build_input(
                term,
                {"venue_diversity": len(venues),
                 "frequency_hits_per_week": float(len(rows))},
                {"hits": evidence["hits"],
                 "cooccurring_chunks": co_chunks},
                {"near_duplicates": [], "covered_by_existing": False})
            fw = evaluate_fn(cfg, fw_input, judge_callable)
            if fw is not None:
                fw = {"verdict": fw["verdict"],
                      "rationale": fw["rationale"],
                      "confidence": fw["confidence"]}
        entry_id = propose_term(
            cfg, term, category="auto-candidate", evidence=evidence,
            firewall=fw, provenance="scanner co-occurrence",
            note=f"auto-proposed from {len(rows)} hits in "
                 f"{', '.join(venues)}; awaiting human review")
        if entry_id is not None:
            known.add(term)
            n += 1
    return n
