"""Advisory-only prompt firewall harness for the IOC updater.

Implements FIREWALL.md sections 1 (input/output schemas), 4 (cost
control), and 5 (failure modes) as code. No live judge endpoint exists
in this build. The harness works fully with the firewall disabled (the
default); the human review queue is the gate. This module makes no
network calls. It is offline by design.

Mode handling:
- off: passthrough to the human queue (no judge call, no log row).
- advisory: attach the judge recommendation to the review entry.
  The judge NEVER promotes; the human decides.
- enforcing: REFUSED. Locked until the firewall passes the
  injection-resistance eval (FIREWALL.md section 5). The settings
  validator also rejects this value; the raise here is defense in
  depth.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import state_path  # noqa: E402

FIREWALL_MODES = ("off", "advisory", "enforcing")

# SAFETY INVARIANT: enforcing stays locked until the firewall passes an
# injection-resistance eval. Do not soften this without that eval.
_ENFORCING_LOCKED_MSG = (
    "enforcing mode is locked until the firewall passes the "
    "injection-resistance eval; see FIREWALL.md section 5"
)

GOLDEN_PATH = (Path(__file__).resolve().parents[2]
               / "references" / "firewall-golden.jsonl")

_VERDICTS = ("ACCEPT", "REJECT", "NARROW")
_CONFIDENCES = ("high", "medium", "low")

# Taint pre-screen regexes (FIREWALL.md section 5.4). Evidence is
# attacker-influenced by design; these markers flag injection attempts.
_TAINT_PATTERNS = [
    re.compile(r"ignore\s+(all|any|previous|prior|above)\s+instructions?",
               re.IGNORECASE),
    re.compile(r"disregard\s+.*instructions?", re.IGNORECASE),
    re.compile(r"\byou are now\b", re.IGNORECASE),
    re.compile(r"new\s+system\s+prompt", re.IGNORECASE),
    re.compile(r"\bas an ai\b", re.IGNORECASE),
    re.compile(r"^\s*(developer|assistant)\s*:", re.IGNORECASE | re.MULTILINE),
]


def _fence_has_system(snippet):
    # Triple-backtick block that also names "system".
    return "```" in snippet and re.search(r"system", snippet, re.IGNORECASE)


def taint_prescreen(snippets):
    """Return True when any snippet carries an injection marker."""
    for s in snippets or []:
        s = str(s)
        if _fence_has_system(s):
            return True
        for pat in _TAINT_PATTERNS:
            if pat.search(s):
                return True
    return False


def build_firewall_input(candidate, mechanical, evidence, list_context):
    """Build the judge input per FIREWALL.md section 1.1.

    candidate: chunk string or dict. mechanical: scorer outputs.
    evidence: hits and co-occurring chunks. list_context: duplicates.
    Sets evidence_tainted via the pre-screen. Snippets are raw and
    untrusted; truncation does not make them safe.
    """
    if isinstance(candidate, dict):
        chunk = str(candidate.get("chunk", ""))
    else:
        chunk = str(candidate)
    mech = dict(mechanical or {})
    ev = dict(evidence or {})
    ctx = dict(list_context or {})
    max_snips = 5
    max_chars = 300
    hits = []
    for h in (ev.get("hits") or [])[:max_snips]:
        h = dict(h)
        h["snippet"] = str(h.get("snippet", ""))[:max_chars]
        hits.append(h)
    co = (ev.get("cooccurring_chunks") or [])[:8]
    tainted = taint_prescreen([h.get("snippet", "") for h in hits])
    return {
        "candidate": {"chunk": chunk, "normalized": chunk.lower(),
                      "tokenizer": "subword-v1"},
        "mechanical": {
            "frequency_hits_per_week":
                float(mech.get("frequency_hits_per_week", 0.0)),
            "novelty_score": float(mech.get("novelty_score", 0.0)),
            "venue_diversity": int(mech.get("venue_diversity", 0)),
            "combined": float(mech.get("combined", 0.0)),
            "threshold": float(mech.get("threshold", 0.50)),
        },
        "evidence": {"evidence_tainted": tainted, "hits": hits,
                     "cooccurring_chunks": co},
        "list_context": {
            "near_duplicates": ctx.get("near_duplicates") or [],
            "covered_by_existing": bool(ctx.get("covered_by_existing",
                                                False)),
        },
        "provenance": {"source": "scanner",
                       "first_seen": datetime.now(timezone.utc).isoformat(),
                       "operator": "tracehound"},
    }


def _invalid(text):
    return {
        "verdict": "REJECT",
        "rationale": "judge output unparseable",
        "benign_use": None,
        "novelty_note": "",
        "actionability": "",
        "narrower_chunk": None,
        "confidence": "low",
        "invalid": True,
        "raw_output": str(text)[:2000],
    }


def parse_judge_output(text, candidate_chunk=None):
    """Strict parser for judge output. Fail closed.

    INVALID (bad JSON, bad verdict, NARROW without a distinct narrower
    chunk) becomes REJECT with rationale "judge output unparseable".
    Rationale longer than 280 chars is truncated, not rejected.
    """
    try:
        if isinstance(text, dict):
            obj = text
        else:
            obj = json.loads(str(text).strip())
    except (json.JSONDecodeError, TypeError):
        return _invalid(text)
    if not isinstance(obj, dict):
        return _invalid(text)
    verdict = obj.get("verdict")
    if verdict not in _VERDICTS:
        return _invalid(text)
    narrower = obj.get("narrower_chunk")
    if verdict == "NARROW":
        if not narrower or not str(narrower).strip():
            return _invalid(text)
        if candidate_chunk and str(narrower) == str(candidate_chunk):
            return _invalid(text)
    confidence = obj.get("confidence")
    if confidence not in _CONFIDENCES:
        confidence = "low"
    return {
        "verdict": verdict,
        "rationale": str(obj.get("rationale", ""))[:280],
        "benign_use": obj.get("benign_use"),
        "novelty_note": str(obj.get("novelty_note", "")),
        "actionability": str(obj.get("actionability", "")),
        "narrower_chunk": (str(narrower) if verdict == "NARROW" else None),
        "confidence": confidence,
    }


def _mode(cfg):
    """Resolve the firewall mode. Unknown values fail closed to off."""
    safety = cfg.get("safety", {})
    if "firewall_mode" in safety:
        mode = str(safety["firewall_mode"]).strip().lower()
    else:
        fw = cfg.get("firewall", {})
        if str(fw.get("enabled", "false")).strip().lower() != "true":
            return "off"
        mode = str(fw.get("mode", "off")).strip().lower()
    return mode if mode in FIREWALL_MODES else "off"


def _budget_state(cfg):
    fw = cfg.get("firewall", {})
    budget = int(fw.get("budget_per_cycle", 50))
    cycle = datetime.now(timezone.utc).strftime("%G-W%V")
    p = state_path(cfg, "firewall_budget.json")
    used = 0
    if p.exists():
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            if doc.get("cycle") == cycle:
                used = int(doc.get("used", 0))
        except (json.JSONDecodeError, ValueError, OSError):
            used = 0
    return cycle, used, budget, p


def _append_log(cfg, row):
    p = state_path(cfg, "firewall_log.jsonl")
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def evaluate(cfg, firewall_input, judge_callable=None):
    """Run one firewall evaluation. Returns the verdict dict or None.

    None means passthrough (mode off, or advisory with no judge
    configured): the candidate goes to the human queue unjudged.
    Enforces the per-cycle budget and appends the decision-log row
    (FIREWALL.md section 3.1). Enforcing mode raises RuntimeError.
    """
    mode = _mode(cfg)
    if mode == "off":
        return None
    if mode == "enforcing":
        # SAFETY INVARIANT: enforcing is locked until the firewall
        # passes the injection-resistance eval. Never bypass this.
        raise RuntimeError(_ENFORCING_LOCKED_MSG)
    cycle, used, budget, budget_path = _budget_state(cfg)
    if used >= budget:
        verdict = {
            "verdict": "DEFER",
            "rationale": ("firewall budget exhausted for this cycle; "
                          "candidate waits for the next cycle"),
            "benign_use": None,
            "novelty_note": "",
            "actionability": "",
            "narrower_chunk": None,
            "confidence": "low",
        }
        _append_log(cfg, _log_row(cfg, firewall_input, verdict, cycle))
        return verdict
    if judge_callable is None:
        # Advisory mode with no judge configured: passthrough.
        return None
    text = judge_callable(firewall_input)
    verdict = parse_judge_output(
        text, firewall_input["candidate"]["chunk"])
    if (firewall_input["evidence"]["evidence_tainted"]
            and verdict["verdict"] == "ACCEPT"):
        # Downgrade: tainted evidence MUST NOT yield a clean ACCEPT.
        verdict["rationale"] = (verdict["rationale"]
                                + " [downgraded: tainted evidence; "
                                + "human review required]")[:280]
        verdict["downgraded"] = True
    _append_log(cfg, _log_row(cfg, firewall_input, verdict, cycle))
    budget_path.write_text(json.dumps({"cycle": cycle, "used": used + 1})
                           + "\n", encoding="utf-8")
    return verdict


def _log_row(cfg, firewall_input, verdict, cycle):
    fw = cfg.get("firewall", {})
    canon = json.dumps(firewall_input, sort_keys=True)
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "candidate": firewall_input["candidate"]["chunk"],
        "verdict": verdict["verdict"],
        "rationale": verdict["rationale"],
        "confidence": verdict["confidence"],
        "mechanical_combined":
            firewall_input["mechanical"]["combined"],
        "judge_model": fw.get("model", "") or "unconfigured",
        "evidence_hash": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
        "evidence_tainted":
            firewall_input["evidence"]["evidence_tainted"],
        "cycle": cycle,
    }


def selftest():
    """Run the parser and taint screen against the golden file.

    No model call is made. Returns 0 when every row passes, else 1.
    """
    if not GOLDEN_PATH.exists():
        print(f"firewall selftest: FAIL: golden file missing: {GOLDEN_PATH}")
        return 1
    passed = failed = 0
    for lineno, line in enumerate(GOLDEN_PATH.read_text(
            encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        ok, why = _check_row(row)
        if ok:
            passed += 1
        else:
            failed += 1
            print(f"firewall selftest: FAIL line {lineno} "
                  f"({row.get('name', '?')}): {why}")
    print(f"firewall selftest: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def _check_row(row):
    kind = row.get("type")
    if kind == "parse":
        got = parse_judge_output(row.get("judge_output"),
                                 row.get("candidate_chunk"))
        if got["verdict"] != row["expected_verdict"]:
            return False, (f"verdict {got['verdict']!r} != "
                           f"{row['expected_verdict']!r}")
        if bool(got.get("invalid")) != bool(row.get("expect_invalid")):
            return False, "invalid flag mismatch"
        if row.get("expected_rationale") is not None and \
                got["rationale"] != row["expected_rationale"]:
            return False, "rationale mismatch"
        if row.get("expect_rationale_len") is not None and \
                len(got["rationale"]) != row["expect_rationale_len"]:
            return False, "rationale length mismatch"
        if row.get("expected_narrower") is not None and \
                got["narrower_chunk"] != row["expected_narrower"]:
            return False, "narrower_chunk mismatch"
        return True, ""
    if kind == "taint":
        got = taint_prescreen(row.get("snippets", []))
        if got != bool(row["expected"]):
            return False, f"tainted={got}, expected={row['expected']}"
        return True, ""
    return False, f"unknown row type: {kind!r}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="run golden-file parser/taint checks (no model)")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    ap.print_help()
    sys.exit(2)
