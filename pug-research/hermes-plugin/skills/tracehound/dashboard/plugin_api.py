"""Tracehound desktop backend: plugin namespace HTTP handler.

Stdlib only. This module is the single enforcement point for the
desktop GUI. It imports the SAME scripts/lib/ modules the CLI uses,
so the GUI and the /tracehound CLI stay two faces of one state:
one config.ini, one state/ dir, one code path, one threat model.

The GUI must never trigger scans except through this module.
Hunts are discrete, human-initiated jobs. There is no cron and no
background schedule in the desktop lane.

Namespace: /api/plugins/tracehound/<endpoint>.
"""

import configparser
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path

NAMESPACE = "/api/plugins/tracehound"

# skills/tracehound/dashboard/plugin_api.py -> skills/tracehound/
SKILL_ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = SKILL_ROOT / "scripts" / "lib"
sys.path.insert(0, str(LIB_DIR))

from config import load_config, ensure_state, state_path  # noqa: E402
from iocs import propose_term, set_status  # noqa: E402

# Worker-2 owns the review queue (iocs.pending_entries and the
# accept/reject/narrow decision writers). Use them when present.
# Fall back to direct set_status plus a local decision log.
try:
    from iocs import (pending_entries as _PENDING,  # noqa: E402
                      accept_term as _ACCEPT,
                      reject_term as _REJECT,
                      narrow_term as _NARROW)
    _W2_REVIEW = True
except ImportError:
    _PENDING = _ACCEPT = _REJECT = _NARROW = None
    _W2_REVIEW = False

# Optional Worker-1 settings validator. Fall back to local validation.
_SETTINGS_VALIDATE = None
try:
    from settings import validate_settings as _SETTINGS_VALIDATE  # noqa: E402
except ImportError:
    _SETTINGS_VALIDATE = None

# Optional Worker-5 case management (entities, relationships,
# indicators). The /cases endpoints return 404 when it is absent.
_CASES = None
_CASES_OK = False
try:
    import cases as _CASES  # noqa: E402
    _CASES_OK = True
except ImportError:
    _CASES = None
    _CASES_OK = False

# Optional Worker-1 hunt runner. Present in this tree. Signature:
# run_hunt(cfg, target, sources, cap, started_by, mock=False).
# It writes live progress to state/jobs/hunt-*.json and honors
# cancel_requested in the job file. The fallback below uses the
# same fetch functions and the same config when it is absent.
_RUN_HUNT = None
_REQUEST_CANCEL = None
_ESTIMATE_HUNT = None
try:
    from sources import (run_hunt as _RUN_HUNT,  # noqa: E402
                         request_cancel as _REQUEST_CANCEL,
                         estimate_hunt as _ESTIMATE_HUNT,
                         HuntRefused)
except ImportError:
    _RUN_HUNT = None
    _REQUEST_CANCEL = None
    _ESTIMATE_HUNT = None

    class HuntRefused(Exception):  # noqa: D101 - fallback only
        pass

# Prompt defaults ship in references/. Overrides live in state/prompts/.
# A PUT writes an override file; a reset deletes it. Defaults are
# never modified.
PROMPT_DEFAULTS = {
    "judge": SKILL_ROOT / "references" / "judge-prompt.md",
    "chat_system": SKILL_ROOT / "references" / "chat-system-prompt.md",
    # Editable default for the hunt query templates. The shipped
    # references/query-templates.md is the read-only seed; an
    # override in state/prompts/ shadows it without editing it.
    "hunt_templates": SKILL_ROOT / "references" / "query-templates.md",
}

# Settings the GUI may write. Firewall mode is locked to advisory/off.
# Any other value is rejected with an explanation, not coerced.
WRITABLE_SECTIONS = {"schedule", "sources", "ioc", "research", "safety",
                     "firewall", "chat", "paths"}
FIREWALL_MODES = {"advisory", "off"}
REVIEW_SLA_DAYS = 7

# Chat intents. Rule-based only. No model call happens on this path.
CHAT_INTENTS = ("hunt", "status", "why", "proposals", "pause", "resume",
                "help")

_JOBS = {}          # job_id -> dict (in-process registry)
_JOBS_LOCK = threading.Lock()
_CANCEL = {}        # job_id -> threading.Event


def _utcnow():
    return datetime.now(timezone.utc).isoformat()


def _load_state_json(cfg, name, default):
    p = state_path(cfg, name)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return default
    return default


def _save_state_json(cfg, name, obj):
    p = state_path(cfg, name)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1) + "\n", encoding="utf-8")
    tmp.replace(p)


def _paused(cfg):
    return cfg.get("safety", {}).get("paused", "false") == "true"


def _config_path():
    p = SKILL_ROOT / "config.ini"
    return p if p.exists() else SKILL_ROOT / "config.example.ini"


def _write_config(cfg_dict):
    # configparser drops comments on rewrite. This is a known
    # limitation; the GUI shows the effective values only.
    cp = configparser.ConfigParser()
    for section, values in cfg_dict.items():
        if section.startswith("_"):
            continue
        cp[section] = {k: str(v) for k, v in values.items()}
    with _config_path().open("w", encoding="utf-8") as f:
        cp.write(f)


def _local_validate_settings(updates):
    """Validate PUT /settings. Returns (ok, message)."""
    for section, values in updates.items():
        if section not in WRITABLE_SECTIONS:
            return False, f"section not writable: {section}"
        if not isinstance(values, dict):
            return False, f"section {section} must be an object"
    fw = updates.get("firewall", {}).get("firewall_mode")
    if fw is not None and fw not in FIREWALL_MODES:
        return False, (
            "firewall_mode is locked to 'advisory' or 'off'. "
            "'enforcing' stays disabled until an injection-resistance "
            "eval passes (FIREWALL.md). The judge reads attacker-"
            "controlled evidence; auto-promotion is not safe."
        )
    for section in ("schedule", "sources"):
        for k, v in updates.get(section, {}).items():
            if k.endswith(("_hours", "_seconds", "_per_query",
                           "_per_sweep", "_chars")):
                try:
                    if float(v) <= 0:
                        return False, f"{section}.{k} must be > 0"
                except (TypeError, ValueError):
                    return False, f"{section}.{k} must be a number"
    return True, "ok"


def _validate_settings(updates):
    if _SETTINGS_VALIDATE is not None:
        return _SETTINGS_VALIDATE(updates)
    return _local_validate_settings(updates)


def _read_hits(cfg, limit=500):
    """Read recent hits from state/hits/*.jsonl, newest first."""
    hits = []
    d = state_path(cfg, "hits")
    if d.exists():
        for jf in sorted(d.glob("*.jsonl"), reverse=True):
            try:
                for line in jf.read_text(encoding="utf-8").splitlines():
                    try:
                        h = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    h.setdefault("file", jf.name)
                    hits.append(h)
                    if len(hits) >= limit:
                        return hits
            except OSError:
                continue
    return hits


def _claim_level(hit, hits):
    """Heuristic claim level for the dashboard.

    The scanner stores raw hits, not ladder levels. Derive a level
    so the GUI can filter and gate toasts. Rule: a URL seen in two
    or more venues, or three or more times, is a burst (L2).
    Everything else is an artifact (L1). Labeled heuristic; the
    reviewer assigns the real level.
    """
    url = hit.get("url", "")
    if not url:
        return "L1"
    venues = {h.get("source") for h in hits if h.get("url") == url}
    count = sum(1 for h in hits if h.get("url") == url)
    if len(venues) >= 2 or count >= 3:
        return "L2"
    return "L1"


def _iocs_records(cfg):
    from iocs import _load
    return _load(cfg)


def _review_entries(cfg):
    """Build the human queue. Worker-2's pending_entries is the
    source of truth when present; the legacy path derives entries
    from proposed working-copy terms."""
    hits = _read_hits(cfg, limit=1000)
    records = {r["term"]: r for r in _iocs_records(cfg)}
    now = datetime.now(timezone.utc)
    entries = []

    def _enrich(term, entry_id, category, proposed_utc, provenance,
               evidence_obj, firewall_obj):
        r = records.get(term, {})
        excerpts = [h for h in hits
                    if term in str(h.get("evidence", "")) or
                    term in str(h.get("url", ""))][:5]
        venues = sorted({h.get("source", "?") for h in excerpts})
        if not venues and isinstance(evidence_obj, dict):
            venues = sorted({h.get("venue", "?") for h in
                             evidence_obj.get("hits", [])})
        try:
            age_days = (now - datetime.fromisoformat(
                proposed_utc or now.isoformat())).days
        except (ValueError, TypeError):
            age_days = 0
        fw = "advisory: human decides"
        if isinstance(firewall_obj, dict) and firewall_obj.get("verdict"):
            fw = (f"judge {firewall_obj['verdict']}: "
                  f"{firewall_obj.get('rationale', '')}")
        return {
            "id": entry_id,
            "term": term,
            "category": category,
            "status": "pending",
            "provenance": provenance or r.get("provenance", ""),
            "added_utc": proposed_utc or r.get("added_utc", ""),
            "note": r.get("note", ""),
            "evidence_excerpts": [
                {"source": h.get("source"), "url": h.get("url", "")[:160],
                 "evidence": str(h.get("evidence", ""))[:300],
                 "observed_utc": h.get("observed_utc", "")}
                for h in excerpts],
            "venue_count": len(venues),
            "venues": venues,
            "cooccurring": (evidence_obj or {}).get("cooccurring_chunks", [])
            if isinstance(evidence_obj, dict) else [],
            "age_days": age_days,
            "sla_breach": age_days > REVIEW_SLA_DAYS,
            "firewall_recommendation": fw,
        }

    if _W2_REVIEW:
        for e in _PENDING(cfg):
            entries.append(_enrich(
                e["term"], e["id"], e.get("category", "proposed"),
                e.get("proposed_utc", ""), "",
                e.get("evidence"), e.get("firewall")))
    else:
        for term, r in records.items():
            if r.get("status") != "proposed":
                continue
            entries.append(_enrich(
                term, term, r.get("category", "proposed"),
                r.get("added_utc", ""), r.get("provenance", ""),
                None, None))
    entries.sort(key=lambda e: (-e["sla_breach"], -e["age_days"]))
    return entries


def _resolve_entry_id(cfg, entry_id_or_term):
    """Accept a review entry id (rv-XXXX) or a term. Returns the id."""
    if _W2_REVIEW:
        for e in _PENDING(cfg):
            if e["id"] == entry_id_or_term or \
                    e["term"] == entry_id_or_term:
                return e["id"]
    return entry_id_or_term


def _apply_review_decision(cfg, entry_id_or_term, verdict,
                           rationale="", narrower_chunk=""):
    """Apply a human decision. Worker-2 functions win when present.

    Worker-2 requires a rationale. The GUI fast path allows an empty
    one; the backend then records an explicit default instead of
    inventing a reason.
    """
    rationale = rationale.strip() or \
        "human decision via desktop UI; no rationale recorded"
    entry_id = _resolve_entry_id(cfg, entry_id_or_term)
    if _W2_REVIEW:
        if verdict == "accept":
            return _ACCEPT(cfg, entry_id, "desktop-human", rationale)
        if verdict == "reject":
            return _REJECT(cfg, entry_id, "desktop-human", rationale)
        if verdict == "narrow":
            if not narrower_chunk:
                raise ValueError("narrow requires narrower_chunk")
            return _NARROW(cfg, entry_id, narrower_chunk,
                           "desktop-human", rationale)
        raise ValueError(f"unknown verdict: {verdict}")
    term = entry_id_or_term
    if verdict == "accept":
        set_status(cfg, term, "active", reason=f"human accept: {rationale}")
    elif verdict == "reject":
        set_status(cfg, term, "inactive",
                   reason=f"human reject: {rationale}")
    elif verdict == "narrow":
        if not narrower_chunk:
            raise ValueError("narrow requires narrower_chunk")
        propose_term(cfg, narrower_chunk,
                     provenance=f"narrowed from {term} by human review",
                     category="proposed",
                     note=f"parent term: {term}; rationale: {rationale}")
        set_status(cfg, term, "proposed",
                   reason=f"superseded-by-narrow: {narrower_chunk}")
    else:
        raise ValueError(f"unknown verdict: {verdict}")
    rec = {"term": term, "verdict": verdict, "rationale": rationale,
           "narrower_chunk": narrower_chunk, "reviewer": "desktop-human",
           "decided_utc": _utcnow()}
    p = state_path(cfg, "review_decisions.jsonl")
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def _estimate_queries(cfg, sources, cap):
    """Estimated query count for a sweep-cap stepper."""
    terms = len(_active_term_list(cfg))
    return min(terms, cap) * len(sources)


def _active_term_list(cfg):
    from iocs import active_terms
    return active_terms(cfg)


def _source_enabled(cfg, name):
    return cfg["sources"].get(f"{name}_enabled", "true") == "true"


def _worker_job_files(cfg):
    """Live job records written by Worker-1's run_hunt."""
    d = state_path(cfg, "jobs")
    out = []
    if d.exists():
        for p in sorted(d.glob("hunt-*.json"), reverse=True):
            try:
                out.append(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
    return out


def _normalize_job(j):
    ps = j.get("per_source", {}) or {}
    done = sum(v.get("done", 0) for v in ps.values())
    total = sum(v.get("total", 0) for v in ps.values())
    hits = sum(v.get("hits", 0) for v in ps.values())
    return {
        "job_id": j.get("job_id", ""),
        "target": j.get("target", ""),
        "sources": j.get("sources", []),
        "status": j.get("status", "unknown"),
        "done": done,
        "total": total or j.get("estimated_queries", 0),
        "new_hits": hits,
        "created_utc": j.get("started_utc") or j.get("created_utc", ""),
        "finished_utc": j.get("finished_utc"),
        "per_source": ps,
        "error": j.get("error"),
        "started_by": j.get("started_by", ""),
    }


def _job_record(job_id):
    with _JOBS_LOCK:
        rec = _JOBS.get(job_id)
    if rec and rec.get("worker_job_id"):
        for wj in _worker_job_files(rec["_cfg"]):
            if wj.get("job_id") == rec["worker_job_id"]:
                return _normalize_job(wj)
    if rec:
        return {k: v for k, v in rec.items() if not k.startswith("_")}
    return {}


def _all_jobs(cfg):
    seen = set()
    out = []
    for wj in _worker_job_files(cfg):
        seen.add(wj.get("job_id"))
        out.append(_normalize_job(wj))
    with _JOBS_LOCK:
        for jid, j in _JOBS.items():
            if j.get("worker_job_id") in seen or jid in seen:
                continue
            out.append({k: v for k, v in j.items()
                        if not k.startswith("_")})
    out.sort(key=lambda j: j.get("created_utc", ""), reverse=True)
    return out


def _job_update(job_id, **fields):
    with _JOBS_LOCK:
        if job_id in _JOBS:
            _JOBS[job_id].update(fields)


def _run_hunt_job(cfg, job_id, target, sources, cap):
    """Execute one discrete human-triggered hunt with cancellation."""
    if _RUN_HUNT is not None:
        # Worker-1's runner owns the loop, the lock, the budget,
        # and the job file. This thread only maps its job id back
        # to the desktop registry so GET /jobs/<id> stays live.
        before = {w.get("job_id") for w in _worker_job_files(cfg)}
        started = _utcnow()
        try:
            _job_update(job_id, status="running", started_utc=started)
            job = _RUN_HUNT(cfg, target=target, sources=sources,
                            cap=cap, started_by="desktop")
        except HuntRefused as e:
            _job_update(job_id, status="failed", error=str(e)[:300],
                        finished_utc=_utcnow())
            return
        except Exception as e:  # noqa: BLE001 - report, never swallow
            _job_update(job_id, status="failed", error=str(e)[:300],
                        finished_utc=_utcnow())
            return
        wid = job.get("job_id", "")
        if wid not in before:
            _job_update(job_id, worker_job_id=wid)
        _job_update(job_id, status=job.get("status", "done"),
                    finished_utc=job.get("finished_utc") or _utcnow())
        return
    # Fallback: same fetch functions and config the CLI uses.
    cancel = _CANCEL[job_id]
    from sources import fetch_urlquery, fetch_cdx, fetch_arquivo
    terms = [target] if target else _active_term_list(cfg)[:cap]
    enabled = [s for s in sources if _source_enabled(cfg, s)]
    total = len(terms) * len(enabled)
    _job_update(job_id, status="running", total=total, done=0,
                new_hits=0,
                per_source={s: {"done": 0, "total": len(terms)}
                            for s in enabled},
                started_utc=_utcnow())
    try:
        fetchers = {"urlquery": lambda t: fetch_urlquery(t, cfg),
                    "cdx": lambda t: fetch_cdx(t, cfg),
                    "arquivo": lambda t: fetch_arquivo(t, cfg)}
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        out = state_path(cfg, "hits", f"{today}.jsonl")
        done = 0
        new_hits = 0
        with out.open("a", encoding="utf-8") as f:
            for s in enabled:
                if cancel.is_set():
                    break
                s_done = 0
                for t in terms:
                    if cancel.is_set():
                        break
                    try:
                        for h in fetchers[s](t):
                            h.setdefault("job_id", job_id)
                            f.write(json.dumps(h) + "\n")
                            new_hits += 1
                    except Exception:  # noqa: BLE001 - one bad query
                        pass           # must not kill the hunt
                    done += 1
                    s_done += 1
                    _job_update(job_id, done=done, new_hits=new_hits)
                    with _JOBS_LOCK:
                        _JOBS[job_id]["per_source"][s]["done"] = s_done
        _job_update(job_id,
                    status="cancelled" if cancel.is_set() else "done",
                    done=done, new_hits=new_hits,
                    finished_utc=_utcnow())
    except Exception as e:  # noqa: BLE001 - report, never swallow
        _job_update(job_id, status="failed", error=str(e)[:300],
                    finished_utc=_utcnow())


def _start_hunt(cfg, target, sources, cap):
    if _paused(cfg):
        raise PermissionError("hunting is paused. Resume first.")
    sources = [s for s in sources
               if s in ("urlquery", "cdx", "arquivo")]
    if not sources:
        raise ValueError("no valid sources requested")
    cap = max(1, int(cap))
    max_cap = int(cfg["sources"].get("max_terms_per_sweep", 200))
    cap = min(cap, max_cap)  # per-source budget cap, never exceeded
    job_id = hashlib.sha256(
        f"{_utcnow()}{target}{sources}{cap}".encode()).hexdigest()[:12]
    try:
        if _ESTIMATE_HUNT is not None:
            est = _ESTIMATE_HUNT(cfg, target, sources, cap)
            estimate = est["total"]
        else:
            estimate = _estimate_queries(cfg, sources, cap)
    except HuntRefused as e:
        raise ValueError(str(e))
    with _JOBS_LOCK:
        _JOBS[job_id] = {"job_id": job_id, "target": target or "",
                         "sources": sources, "cap": cap,
                         "estimate_queries": estimate,
                         "status": "queued", "done": 0, "total": estimate,
                         "new_hits": 0, "created_utc": _utcnow(),
                         "worker_job_id": None,
                         "_cfg": cfg}
    _CANCEL[job_id] = threading.Event()
    t = threading.Thread(target=_run_hunt_job,
                         args=(cfg, job_id, target, sources, cap),
                         daemon=True)
    t.start()
    return {"job_id": job_id, "estimate_queries": estimate,
            "status": "queued"}


def _stop_hunt(cfg, job_id):
    with _JOBS_LOCK:
        rec = _JOBS.get(job_id)
    if rec and rec.get("worker_job_id") and _REQUEST_CANCEL is not None:
        # Worker-1's cancel path: flags cancel_requested in the job
        # file. The loop stops between queries.
        return _REQUEST_CANCEL(cfg, rec["worker_job_id"])
    ev = _CANCEL.get(job_id)
    if ev is None:
        return False
    ev.set()
    return True


# --- Prompts: defaults in references/, overrides in state/prompts/ ---

def _prompt_text_for(cfg, name):
    if name not in PROMPT_DEFAULTS:
        raise KeyError(name)
    override = state_path(cfg, "prompts", PROMPT_DEFAULTS[name].name)
    if override.exists():
        return override.read_text(encoding="utf-8"), "override"
    default = PROMPT_DEFAULTS[name]
    if default.exists():
        return default.read_text(encoding="utf-8"), "default"
    return "", "missing"


def _prompt_write(cfg, name, text):
    if name not in PROMPT_DEFAULTS:
        raise KeyError(name)
    d = state_path(cfg, "prompts")
    d.mkdir(parents=True, exist_ok=True)
    (d / PROMPT_DEFAULTS[name].name).write_text(text, encoding="utf-8")


def _prompt_reset(cfg, name):
    if name not in PROMPT_DEFAULTS:
        raise KeyError(name)
    p = state_path(cfg, "prompts", PROMPT_DEFAULTS[name].name)
    if p.exists():
        p.unlink()
    return _prompt_text_for(cfg, name)


# --- Chat: rule-based responder first, optional model path ---

def _chat_mode(cfg):
    """Report which chat brain is active. The GUI shows this."""
    chat = cfg.get("chat", {})
    if chat.get("model_enabled", "false") == "true" and chat.get("endpoint"):
        key_env = chat.get("api_key_env", "TRACEHOUND_CHAT_KEY")
        if os.environ.get(key_env):
            return {"mode": "model", "endpoint": chat["endpoint"],
                    "model": chat.get("model", ""),
                    "detail": "optional model path active"}
        return {"mode": "rule",
                "detail": f"model enabled but {key_env} not set"}
    return {"mode": "rule",
            "detail": "rule-based responder, zero model dependency"}


def _chat_model_reply(cfg, system_prompt, history, message):
    """Optional model path. Same env-var-key pattern as the firewall
    judge: the key lives in the environment, never in config."""
    chat = cfg.get("chat", {})
    endpoint = chat["endpoint"]
    key = os.environ.get(chat.get("api_key_env", "TRACEHOUND_CHAT_KEY"), "")
    payload = {
        "model": chat.get("model", ""),
        "messages": ([{"role": "system", "content": system_prompt}] +
                     history[-10:] +
                     [{"role": "user", "content": message}]),
    }
    cmd = ["curl", "-s", "--max-time", "60", "-X", "POST", endpoint,
           "-H", "Content-Type: application/json",
           "-H", f"Authorization: Bearer {key}",
           "-d", json.dumps(payload)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        data = json.loads(r.stdout)
        return data["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return None


def _chat_rule(cfg, message):
    """Rule-based intents. Returns (text, cards, action)."""
    msg = message.strip()
    low = msg.lower()
    cards = []
    action = None

    if low.startswith("hunt ") or low == "hunt":
        # "hunt zz=oai on urlquery" -> term + source. This message IS
        # the human initiating. No autonomous work happens otherwise.
        rest = msg[4:].strip()
        sources = ["urlquery", "cdx", "arquivo"]
        for s in ("urlquery", "cdx", "arquivo"):
            if f"on {s}" in low or f" {s}" in low.split():
                sources = [s]
                rest = re.sub(rf"\s+on\s+{s}\s*$", "", rest,
                              flags=re.IGNORECASE).strip()
        term = rest.split()[0] if rest.split() else ""
        cap = int(cfg["sources"].get("max_terms_per_sweep", 200))
        try:
            job = _start_hunt(cfg, term, sources, cap)
            action = {"type": "hunt_started", "job_id": job["job_id"]}
            text = (f"Hunt started for '{term or 'active list'}' on "
                    f"{', '.join(sources)}. Job {job['job_id']}, "
                    f"about {job['estimate_queries']} queries. "
                    f"Watch progress on the Hunt page.")
        except (PermissionError, ValueError) as e:
            text = f"Cannot start hunt: {e}"
        return text, cards, action

    if any(k in low for k in ("what did you find", "any hits", "status",
                              "how is the hunt", "progress")):
        hits = _read_hits(cfg, limit=200)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        todays = [h for h in hits
                  if str(h.get("observed_utc", "")).startswith(today)]
        queue = _review_entries(cfg)
        jobs = sorted(_JOBS.values(),
                      key=lambda j: j.get("created_utc", ""), reverse=True)
        last = jobs[0] if jobs else None
        last_line = ("no hunts yet this session"
                     if not last else
                     f"last hunt {last['job_id']} "
                     f"({last.get('status')}, {last.get('new_hits', 0)} "
                     f"new hits)")
        text = (f"Today: {len(todays)} hits. "
                f"Review queue: {len(queue)} waiting. {last_line}.")
        return text, cards, action

    if low.startswith("why") and ("flag" in low or "candidate" in low):
        # "why was candidate X flagged?" -> evidence + rationale.
        term = None
        m = re.search(r"['\"]([^'\"]+)['\"]", msg)
        if m:
            term = m.group(1)
        else:
            words = [w for w in re.split(r"\s+", msg)
                     if len(w) >= 4 and w not in
                     ("was", "were", "flagged", "candidate", "this", "that")]
            term = words[-1] if words else None
        if not term:
            return ("Name the candidate, e.g. \"why was 'zzbulk' "
                    "flagged?\""), cards, action
        records = {r["term"]: r for r in _iocs_records(cfg)}
        rec = records.get(term)
        if not rec:
            return (f"'{term}' is not in the working IOC list. "
                    "It was never proposed, or it was rejected."), cards, action
        excerpts = [h for h in _read_hits(cfg, limit=1000)
                    if term in str(h.get("evidence", ""))][:3]
        lines = [f"'{term}' is {rec['status']}. "
                 f"Provenance: {rec.get('provenance', 'unknown')}."]
        for h in excerpts:
            lines.append(f"- {h.get('source')}: "
                         f"{str(h.get('evidence', ''))[:160]}")
        pending = [e for e in _review_entries(cfg) if e["term"] == term]
        if pending:
            e = pending[0]
            lines.append(f"It waits in the review queue as {e['id']}. "
                         f"Firewall: {e['firewall_recommendation']}. "
                         "No auto-promotion.")
            cards = [{"entry_id": e["id"], "term": term,
                      "kind": "review_inline",
                      "provenance": e["provenance"],
                      "age_days": e["age_days"],
                      "sla_breach": e["sla_breach"]}]
        elif rec.get("status") == "quarantined":
            lines.append("It is quarantined: proposed but awaiting "
                         "review. Nothing promotes it without your accept.")
        return "\n".join(lines), cards, action

    if low in ("proposals", "review queue", "show queue", "candidates"):
        entries = _review_entries(cfg)[:10]
        if not entries:
            return "The review queue is empty.", cards, action
        cards = [{"entry_id": e["id"], "term": e["term"],
                  "kind": "review_inline",
                  "provenance": e["provenance"],
                  "age_days": e["age_days"],
                  "sla_breach": e["sla_breach"]} for e in entries]
        text = f"{len(entries)} terms wait in the review queue. " \
               f"Accept, reject, or narrow each below."
        return text, cards, action

    if low.startswith("pause"):
        cfg_d = load_config()
        cfg_d.setdefault("safety", {})["paused"] = "true"
        _write_config(cfg_d)
        return "All hunting paused. The kill switch is on.", cards, action

    if low.startswith("resume"):
        cfg_d = load_config()
        cfg_d.setdefault("safety", {})["paused"] = "false"
        _write_config(cfg_d)
        return "Hunting resumed.", cards, action

    if low in ("help", "?"):
        return ("I understand: 'hunt <term> [on urlquery|cdx|arquivo]', "
                "'what did you find?', \"why was '<term>' flagged?\", "
                "'show queue', 'pause', 'resume'. Every promotion still "
                "needs your explicit accept click."), cards, action

    return ("I did not catch that. Try 'help' for what I understand. "
            "I never hunt on my own; a 'hunt ...' message is you "
            "starting one."), cards, action


def _chat(cfg, message, history):
    system_prompt, _ = _prompt_text_for(cfg, "chat_system")
    mode = _chat_mode(cfg)
    text, cards, action = _chat_rule(cfg, message)
    model_text = None
    if mode["mode"] == "model":
        model_text = _chat_model_reply(cfg, system_prompt, history, message)
    reply = {"role": "assistant", "text": model_text or text,
             "rule_text": text, "cards": cards, "action": action,
             "mode": mode["mode"], "utc": _utcnow()}
    p = state_path(cfg, "chat.jsonl")
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"role": "user", "text": message,
                            "utc": _utcnow()}) + "\n")
        f.write(json.dumps(reply) + "\n")
    return reply


# --- Research check-now ---

def _research_check(cfg):
    from research import check_watchlist
    seen_before = _load_state_json(cfg, "research_seen.json", {})
    n = check_watchlist(cfg)
    seen_after = _load_state_json(cfg, "research_seen.json", {})
    changed = [u for u in seen_after if seen_before.get(u) != seen_after[u]]
    return {"proposed": n, "changed_urls": changed,
            "checked_utc": _utcnow()}


# --- HTTP plumbing ---

class Handler(BaseHTTPRequestHandler):
    server_version = "TracehoundPlugin/0.1"

    def log_message(self, fmt, *args):  # keep logs quiet
        pass

    def _cfg(self):
        cfg = load_config()
        ensure_state(cfg)
        return cfg

    def _path(self):
        p = urllib.parse.urlparse(self.path).path
        if p.startswith(NAMESPACE):
            p = p[len(NAMESPACE):]
        return p or "/"

    def _send(self, code, obj, ctype="application/json"):
        body = obj if isinstance(obj, str) else json.dumps(obj)
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            n = 0
        raw = self.rfile.read(n) if n else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def _query(self):
        return urllib.parse.parse_qs(
            urllib.parse.urlparse(self.path).query)

    def _case_db(self, cfg):
        # Case DB helpers. The case layer is the system of record
        # for entities/relationships/indicators only. It never
        # touches the IOC list or the review queue.
        if not _CASES_OK:
            raise RuntimeError("case layer unavailable")
        return _CASES.connect(cfg=cfg)

    def _case_404(self):
        self._send(404, {"error": "case layer unavailable"})

    def _guard(self):
        """Paused state short-circuits every scan-triggering call."""
        cfg = self._cfg()
        return cfg, _paused(cfg)

    # -- GET --

    def do_GET(self):
        p = self._path()
        cfg = self._cfg()
        try:
            if p == "/hits":
                hits = _read_hits(cfg)
                for h in hits:
                    h["claim_level"] = h.get("claim_level") or \
                        _claim_level(h, hits)
                self._send(200, {"hits": hits[:500],
                                "total": len(hits)})
            elif p == "/iocs":
                self._send(200, {"iocs": _iocs_records(cfg)})
            elif p == "/iocs/export":
                body = json.dumps({"exported_utc": _utcnow(),
                                   "iocs": _iocs_records(cfg)}, indent=1)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Disposition",
                                 "attachment; filename=tracehound-iocs.json")
                self.send_header("Content-Length", str(len(body.encode())))
                self.end_headers()
                self.wfile.write(body.encode("utf-8"))
            elif p == "/review":
                self._send(200, {"entries": _review_entries(cfg),
                                 "sla_days": REVIEW_SLA_DAYS})
            elif p == "/candidates":
                cands = []
                d = state_path(cfg, "candidates")
                if d.exists():
                    for jf in sorted(d.glob("*.jsonl"), reverse=True)[:7]:
                        for line in jf.read_text(
                                encoding="utf-8").splitlines()[-200:]:
                            try:
                                cands.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
                self._send(200, {"candidates": cands})
            elif p == "/jobs":
                self._send(200, {"jobs": _all_jobs(cfg)})
            elif p.startswith("/jobs/"):
                rec = _job_record(p[len("/jobs/"):])
                if not rec:
                    self._send(404, {"error": "unknown job"})
                else:
                    rec.pop("_cfg", None)
                    self._send(200, rec)
            elif p == "/settings":
                out = {s: dict(cfg[s]) for s in cfg.sections()
                       if not s.startswith("_")}
                out["_chat_mode"] = _chat_mode(cfg)
                self._send(200, out)
            elif p == "/diagnostics":
                self._send(200, _diagnostics(cfg))
            elif p == "/prompts":
                self._send(200, {
                    name: {"source": _prompt_text_for(cfg, name)[1]}
                    for name in PROMPT_DEFAULTS})
            elif p.startswith("/prompts/"):
                name = p[len("/prompts/"):]
                try:
                    text, source = _prompt_text_for(cfg, name)
                except KeyError:
                    self._send(404, {"error": "unknown prompt"})
                    return
                self._send(200, {"name": name, "text": text,
                                 "source": source})
            elif p == "/chat":
                hist = []
                cp = state_path(cfg, "chat.jsonl")
                if cp.exists():
                    for line in cp.read_text(
                            encoding="utf-8").splitlines()[-100:]:
                        try:
                            hist.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                self._send(200, {"history": hist,
                                 "chat_mode": _chat_mode(cfg)})
            elif p == "/cases/entities":
                if not _CASES_OK:
                    self._case_404()
                    return
                etype = self._query().get("type", [None])[0]
                try:
                    ents = _CASES.list_entities(self._case_db(cfg), etype)
                except ValueError as e:
                    self._send(400, {"error": str(e)})
                    return
                self._send(200, {"entities": ents})
            elif p.startswith("/cases/entities/"):
                if not _CASES_OK:
                    self._case_404()
                    return
                eid = urllib.parse.unquote(p[len("/cases/entities/"):])
                db = self._case_db(cfg)
                ent = _CASES.get_entity(db, eid)
                if not ent:
                    self._send(404, {"error": "unknown entity"})
                    return
                inds = _CASES.list_indicators(db, eid)
                nbrs = _CASES.neighbors(db, eid) or {}
                self._send(200, {"entity": ent, "indicators": inds,
                                 "links": nbrs.get("links", []),
                                 "adjacent": nbrs.get("adjacent", {})})
            elif p == "/cases/graph":
                if not _CASES_OK:
                    self._case_404()
                    return
                g = _CASES.graph(self._case_db(cfg))
                # Contract shape: edges use from/to (DB uses from_id/to_id).
                edges = [{"id": e["id"], "from": e["from_id"],
                          "to": e["to_id"], "rel": e["rel"]}
                         for e in g["edges"]]
                self._send(200, {"nodes": g["nodes"], "edges": edges})
            else:
                self._send(404, {"error": "unknown endpoint"})
        except Exception as e:  # noqa: BLE001 - never leak a traceback
            self._send(500, {"error": str(e)[:300]})

    # -- POST --

    def do_POST(self):
        p = self._path()
        cfg = self._cfg()
        body = self._body()
        try:
            if p == "/hunt/start":
                try:
                    res = _start_hunt(
                        cfg, body.get("target", ""),
                        body.get("sources",
                                 ["urlquery", "cdx", "arquivo"]),
                        body.get("cap", 200))
                except PermissionError as e:
                    self._send(403, {"error": str(e)})
                    return
                except ValueError as e:
                    self._send(400, {"error": str(e)})
                    return
                self._send(200, res)
            elif p == "/hunt/stop":
                job_id = body.get("job_id", "")
                ok = _stop_hunt(cfg, job_id)
                self._send(200 if ok else 404,
                           {"stopped": ok, "job_id": job_id})
            elif p == "/review/decision":
                try:
                    rec = _apply_review_decision(
                        cfg, body.get("id", ""), body.get("verdict", ""),
                        rationale=body.get("rationale", ""),
                        narrower_chunk=body.get("narrower_chunk", ""))
                except ValueError as e:
                    self._send(400, {"error": str(e)})
                    return
                self._send(200, {"decision": rec})
            elif p == "/iocs":
                term = (body.get("term") or "").strip()
                if not term:
                    self._send(400, {"error": "term required"})
                    return
                # Manual adds enter as proposed. They never skip
                # the review queue.
                new = propose_term(cfg, term, provenance="human manual add",
                                   category=body.get("category", "proposed"),
                                   note=body.get("note", ""))
                self._send(200, {"term": term, "proposed": new})
            elif p == "/iocs/bulk-import":
                terms = body.get("terms", [])
                added, skipped = 0, 0
                for t in terms:
                    t = str(t).strip()
                    if not t:
                        continue
                    if propose_term(cfg, t, provenance="human bulk import"):
                        added += 1
                    else:
                        skipped += 1
                self._send(200, {"added": added, "skipped": skipped})
            elif p.startswith("/iocs/") and p.endswith("/demote"):
                term = urllib.parse.unquote(p[len("/iocs/"):-len("/demote")])
                ok = set_status(cfg, term, "inactive",
                                reason=body.get("reason", "human demote"))
                self._send(200 if ok else 404, {"demoted": ok})
            elif p == "/research/check":
                if _paused(cfg):
                    self._send(403, {"error": "hunting is paused"})
                    return
                self._send(200, _research_check(cfg))
            elif p == "/chat":
                message = (body.get("message") or "").strip()
                if not message:
                    self._send(400, {"error": "message required"})
                    return
                hist_path = state_path(cfg, "chat.jsonl")
                history = []
                if hist_path.exists():
                    for line in hist_path.read_text(
                            encoding="utf-8").splitlines()[-20:]:
                        try:
                            r = json.loads(line)
                            if r.get("role") in ("user", "assistant"):
                                history.append(
                                    {"role": r["role"],
                                     "content": r.get("text", "")})
                        except json.JSONDecodeError:
                            continue
                self._send(200, _chat(cfg, message, history))
            elif p.startswith("/prompts/") and p.endswith("/reset"):
                name = p[len("/prompts/"):-len("/reset")]
                try:
                    text, source = _prompt_reset(cfg, name)
                except KeyError:
                    self._send(404, {"error": "unknown prompt"})
                    return
                self._send(200, {"name": name, "text": text,
                                 "source": source})
            elif p == "/settings/pause":
                cfg_d = load_config()
                cfg_d.setdefault("safety", {})["paused"] = \
                    "true" if body.get("paused") else "false"
                _write_config(cfg_d)
                self._send(200, {"paused": _paused(load_config())})
            elif p == "/settings/reset":
                # Danger zone: restore config.example.ini defaults.
                # state/ is untouched. Prompts overrides stay.
                src = SKILL_ROOT / "config.example.ini"
                dst = SKILL_ROOT / "config.ini"
                if src.exists():
                    dst.write_text(src.read_text(encoding="utf-8"),
                                   encoding="utf-8")
                    self._send(200, {"ok": True})
                else:
                    self._send(500, {"error": "config.example.ini missing"})
            elif p == "/cases/entities":
                if not _CASES_OK:
                    self._case_404()
                    return
                etype = (body.get("type") or "").strip()
                label = (body.get("label") or "").strip()
                db = self._case_db(cfg)
                try:
                    if etype == "trace" and body.get("trace_text"):
                        # Traces run indicator extraction on save.
                        # Extraction populates the case DB only;
                        # it never touches the IOC list.
                        eid = _CASES.add_trace(
                            db, label, body.get("trace_text", ""),
                            provenance=body.get("provenance", ""),
                            job_id=body.get("job_id"))
                    else:
                        eid = _CASES.add_entity(
                            db, etype, label,
                            data=body.get("data"),
                            provenance=body.get("provenance", ""))
                except ValueError as e:
                    self._send(400, {"error": str(e)})
                    return
                self._send(201, {"entity": _CASES.get_entity(db, eid)})
            elif p == "/cases/link":
                if not _CASES_OK:
                    self._case_404()
                    return
                try:
                    lid = _CASES.link(
                        self._case_db(cfg), body.get("from_id", ""),
                        body.get("to_id", ""), body.get("rel", ""))
                except ValueError as e:
                    self._send(400, {"error": str(e)})
                    return
                self._send(201, {"link_id": lid})
            elif p == "/cases/extract":
                # Indicator preview. Read-only: nothing is saved.
                if not _CASES_OK:
                    self._case_404()
                    return
                inds = _CASES.extract_indicators(body.get("trace_text", ""))
                self._send(200, {"indicators": [
                    {"kind": k, "value": v} for k, v in inds]})
            else:
                self._send(404, {"error": "unknown endpoint"})
        except Exception as e:  # noqa: BLE001 - never leak a traceback
            self._send(500, {"error": str(e)[:300]})

    # -- PUT --

    def do_PUT(self):
        p = self._path()
        body = self._body()
        try:
            if p == "/settings":
                ok, msg = _validate_settings(body)
                if not ok:
                    self._send(400, {"error": msg})
                    return
                cfg_d = load_config()
                for section, values in body.items():
                    cfg_d.setdefault(section, {}).update(
                        {k: str(v) for k, v in values.items()})
                _write_config(cfg_d)
                self._send(200, {"ok": True})
            elif p.startswith("/prompts/"):
                name = p[len("/prompts/"):]
                if name not in PROMPT_DEFAULTS:
                    self._send(404, {"error": "unknown prompt"})
                    return
                text = body.get("text", "")
                if not isinstance(text, str) or not text.strip():
                    self._send(400, {"error": "text required"})
                    return
                cfg = self._cfg()
                _prompt_write(cfg, name, text)
                self._send(200, {"name": name, "source": "override"})
            elif p.startswith("/cases/entities/"):
                if not _CASES_OK:
                    self._case_404()
                    return
                eid = urllib.parse.unquote(p[len("/cases/entities/"):])
                db = self._case_db(self._cfg())
                ok = _CASES.update_entity(
                    db, eid, label=body.get("label"),
                    data=body.get("data"),
                    provenance=body.get("provenance"))
                if not ok:
                    self._send(404, {"error": "unknown entity"})
                    return
                self._send(200, {"entity": _CASES.get_entity(db, eid)})
            else:
                self._send(404, {"error": "unknown endpoint"})
        except Exception as e:  # noqa: BLE001 - never leak a traceback
            self._send(500, {"error": str(e)[:300]})

    # -- DELETE --

    def do_DELETE(self):
        p = self._path()
        try:
            if p.startswith("/cases/entities/"):
                if not _CASES_OK:
                    self._case_404()
                    return
                eid = urllib.parse.unquote(p[len("/cases/entities/"):])
                # Cascade: relationships and indicators go with the
                # entity. The IOC list is never touched (cases.py).
                ok = _CASES.delete_entity(self._case_db(self._cfg()), eid)
                self._send(200 if ok else 404, {"deleted": ok})
            elif p.startswith("/cases/link/"):
                if not _CASES_OK:
                    self._case_404()
                    return
                lid = urllib.parse.unquote(p[len("/cases/link/"):])
                ok = _CASES.unlink(self._case_db(self._cfg()), lid)
                self._send(200 if ok else 404, {"deleted": ok})
            else:
                self._send(404, {"error": "unknown endpoint"})
        except Exception as e:  # noqa: BLE001 - never leak a traceback
            self._send(500, {"error": str(e)[:300]})


def _diagnostics(cfg):
    """Backend health for the GUI status indicator."""
    import shutil
    diag = {"backend": "connected",
            "config_source": cfg.get("_config_source", "unknown"),
            "paused": _paused(cfg),
            "curl": bool(shutil.which("curl")),
            "lib": {}}
    for mod in ("config", "iocs", "sources", "predict", "research"):
        try:
            __import__(mod)
            diag["lib"][mod] = "ok"
        except ImportError:
            diag["lib"][mod] = "missing"
    diag["worker1_run_hunt"] = "present" if _RUN_HUNT else "fallback"
    diag["worker2_review"] = "present" if _W2_REVIEW else "fallback"
    diag["worker5_cases"] = "present" if _CASES_OK else "missing"
    diag["settings_validate"] = "present" if _SETTINGS_VALIDATE \
        else "fallback"
    diag["chat_mode"] = _chat_mode(cfg)
    diag["prompts"] = {n: _prompt_text_for(cfg, n)[1]
                       for n in PROMPT_DEFAULTS}
    return diag


def run(host="127.0.0.1", port=0):
    """Start the handler. The Hermes host mounts this module and
    serves NAMESPACE. Direct runs are for tests only."""
    from http.server import HTTPServer
    srv = HTTPServer((host, port), Handler)
    print(f"tracehound plugin API on {srv.server_address}")
    srv.serve_forever()


if __name__ == "__main__":
    run()
