"""Discrete hunt jobs across three public sources.

Every hunt is human-triggered. No scheduler lives here. The scanner
points at public sources, writes hits and query outcomes to state/,
and stops when the human cancels or pauses. Stdlib only. Read-only
GETs via curl against an allowlist of hosts.
"""

import json
import os
import re
import secrets
import subprocess
import tempfile
import time
import urllib.parse
from datetime import datetime, timezone

from config import state_path

ALLOWLIST = {
    "urlquery.net",
    "web.archive.org",
    "arquivo.pt",
    "transluce.org",
}

URLQUERY_SEARCH = "https://urlquery.net/api/v1/search"
CDX_SEARCH = "https://web.archive.org/cdx/search/cdx"
ARQUIVO_CDX = "https://arquivo.pt/wayback/cdx"

SOURCE_NAMES = ("urlquery", "cdx", "arquivo")

# Nonce terms ride one shared relay-prefix query per batch (CDX-2/CDX-3).
_NONCE_BATCH_SIZE = 6
# Mock delay keeps cancel-path tests deterministic. Real runs use the
# configured request delay.
_MOCK_DELAY = 0.01


class HuntRefused(Exception):
    """Raised when a hunt request breaks a guardrail."""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _host_allowed(url):
    host = urllib.parse.urlparse(url).hostname or ""
    return any(host == a or host.endswith("." + a) for a in ALLOWLIST)


def _split_status(stdout):
    # curl -w appends the bare status code after the headers.
    m = re.search(r"(\d{3})\s*$", stdout or "")
    if not m:
        return 0, stdout or ""
    return int(m.group(1)), stdout[:m.start()].rstrip()


def _curl_once(url, cfg, params=None):
    """Run one GET. Returns (http_status, headers_text, body_bytes)."""
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    if not _host_allowed(url):
        raise ValueError(f"host not allowlisted: {url}")
    ua = cfg["sources"].get("user_agent", "tracehound/0.1")
    fd, body_path = tempfile.mkstemp(prefix="th-", suffix=".body")
    os.close(fd)
    try:
        cmd = ["curl", "-s", "-D", "-", "-o", body_path, "-w", "%{http_code}",
               "--max-time", "60", "-A", ua, url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        status, headers = _split_status(r.stdout)
        body = b""
        try:
            with open(body_path, "rb") as f:
                body = f.read()
        except OSError:
            pass
        if r.returncode != 0 and not body:
            return 0, "", b""
        return status, headers, body
    finally:
        try:
            os.remove(body_path)
        except OSError:
            pass


def _retry_after(headers):
    m = re.search(r"(?im)^retry-after:\s*(\d+)", headers or "")
    return int(m.group(1)) if m else None


def _log_throttle(cfg, source, term, status):
    # Every 429/403 is logged. Throttles MUST NOT become negatives.
    rec = {"ts": _now(), "source": source, "term": term, "status": status}
    with state_path(cfg, "throttles.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _curl_json(url, cfg, params=None, source="", term=""):
    """GET with full status handling.

    Returns (outcome, http_status, parsed_json_or_None).
    outcome is one of "ok", "throttled", "error".
    A throttled or failed query is NEVER reported as "no hits".
    """
    delay = float(cfg["sources"].get("request_delay_seconds", 5))
    attempts = 3
    for attempt in range(attempts):
        status, headers, body = _curl_once(url, cfg, params)
        time.sleep(delay)
        if status == 200:
            try:
                return "ok", status, json.loads(body.decode("utf-8", "replace") or "null")
            except (json.JSONDecodeError, UnicodeDecodeError):
                return "error", status, None
        if status in (429, 403):
            _log_throttle(cfg, source, term, status)
            if attempt < attempts - 1:
                wait = _retry_after(headers)
                if wait is None:
                    wait = min(120.0, max(delay, 5.0) * (2 ** attempt))
                time.sleep(wait)
                continue
            return "throttled", status, None
        if 500 <= status <= 599:
            # One retry on server errors, then record an error.
            if attempt == 0:
                time.sleep(delay)
                continue
            return "error", status, None
        # Other statuses (curl failure, 4xx): an error, not a negative.
        return "error", status, None
    return "throttled", 0, None


def _is_hostname_term(term):
    return "." in term and "=" not in term and " " not in term and "/" not in term


def _cursor_param(source, cursor):
    # urlquery takes date=[YYYY-MM-DD TO *]; CDX takes from=YYYYMMDDHHMMSS.
    if not cursor:
        return {}
    try:
        dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
    except ValueError:
        return {}
    if source == "urlquery":
        return {"date": f"[{dt.strftime('%Y-%m-%d')} TO *]"}
    return {"from": dt.strftime("%Y%m%d%H%M%S")}


def build_queries(cfg, source, terms, cursor):
    """Build the query list for one source. No network happens here."""
    if source not in SOURCE_NAMES:
        raise ValueError(f"unknown source: {source}")
    limit = int(cfg["sources"].get("max_results_per_query", 50))
    queries = []
    if source == "urlquery":
        for t in terms:
            params = {"q": t, "format": "json"}
            params.update(_cursor_param(source, cursor))
            queries.append({"id": f"uq:{t}", "terms": [t], "label": t,
                            "url": URLQUERY_SEARCH, "params": params})
        return queries
    # cdx / arquivo: hostname terms become prefix sweeps; nonce-grammar
    # terms ride batched relay-prefix queries (templates CDX-2, CDX-3).
    base = CDX_SEARCH if source == "cdx" else ARQUIVO_CDX
    field = "urlkey" if source == "cdx" else "original"
    for t in terms:
        if _is_hostname_term(t):
            params = {"url": t + "/*", "matchType": "prefix",
                      "output": "json", "limit": limit}
            params.update(_cursor_param(source, cursor))
            queries.append({"id": f"{source}:host:{t}", "terms": [t],
                            "label": t, "url": base, "params": params})
    nonce = [t for t in terms if not _is_hostname_term(t)]
    for i in range(0, len(nonce), _NONCE_BATCH_SIZE):
        batch = nonce[i:i + _NONCE_BATCH_SIZE]
        alt = "|".join(re.escape(t) for t in batch)
        params = {"url": "r.jina.ai/http*", "matchType": "prefix",
                  "output": "json", "limit": limit,
                  "filter": f"{field}:.*({alt}).*"}
        params.update(_cursor_param(source, cursor))
        queries.append({"id": f"{source}:nonce:{i // _NONCE_BATCH_SIZE}",
                        "terms": batch, "label": "nonce-batch",
                        "url": base, "params": params})
    return queries


def _mock_fetch(query):
    # Dry run. Returns synthetic data; MUST NOT touch the network.
    time.sleep(_MOCK_DELAY)
    return "ok", 200, [{"url": "https://example.com/mock/" + query["id"],
                        "report_url": "", "mock": True}]


def fetch_query(cfg, source, query, mock=False):
    """Run one query. Returns (outcome, http_status, hit_rows)."""
    if mock:
        outcome, status, rows = _mock_fetch(query)
    else:
        outcome, status, data = _curl_json(query["url"], cfg, query["params"],
                                          source=source,
                                          term=",".join(query["terms"][:3]))
        rows = data if isinstance(data, list) else []
    hits = []
    if outcome == "ok":
        if source == "urlquery":
            for row in rows if isinstance(rows, list) else []:
                if not isinstance(row, dict):
                    continue
                hits.append({
                    "source": source,
                    "query_id": query["id"],
                    "term": query["terms"][0] if query["terms"] else "",
                    "url": row.get("url") or row.get("report_url", ""),
                    "observed_utc": _now(),
                    "evidence": str(row)[:500],
                })
        else:
            # CDX-style: first row is the header.
            if rows and len(rows) >= 2:
                header, body = rows[0], rows[1:]
                for r in body:
                    rec = dict(zip(header, r)) if isinstance(r, list) else {}
                    hits.append({
                        "source": source,
                        "query_id": query["id"],
                        "term": query["label"],
                        "url": rec.get("original", ""),
                        "observed_utc": _now(),
                        "evidence": ("timestamp=%s status=%s digest=%s"
                                     % (rec.get("timestamp"), rec.get("statuscode"),
                                        rec.get("digest", ""))),
                    })
    return outcome, status, hits


def _load_cursors(cfg):
    p = state_path(cfg, "cursors.json")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cursors(cfg, cursors):
    state_path(cfg, "cursors.json").write_text(
        json.dumps(cursors, indent=1) + "\n", encoding="utf-8")


def _job_path(cfg, job_id):
    return state_path(cfg, "jobs", f"{job_id}.json")


def _write_job(cfg, job):
    _job_path(cfg, job["job_id"]).write_text(
        json.dumps(job, indent=1) + "\n", encoding="utf-8")


def _read_job(cfg, job_id):
    p = _job_path(cfg, job_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _paused(cfg):
    return cfg.get("safety", {}).get("paused", "false") == "true"


def select_terms(cfg, target, cap):
    """Pick active terms for a hunt. Cap is enforced by the caller."""
    from iocs import active_terms
    terms = active_terms(cfg)
    t = (target or "all").strip().lower()
    if t and t != "all":
        terms = [x for x in terms if t in x.lower()]
    return terms[:cap]


def estimate_hunt(cfg, target, sources, cap):
    """Count planned queries per source. No network happens here."""
    for s in sources:
        if s not in SOURCE_NAMES:
            raise ValueError(f"unknown source: {s}")
    max_terms = int(cfg["sources"].get("max_terms_per_sweep", 200))
    if cap > max_terms:
        raise HuntRefused(
            f"cap {cap} exceeds max_terms_per_sweep {max_terms}; refusing")
    terms = select_terms(cfg, target, cap)
    cursors = _load_cursors(cfg)
    per_source = {}
    total = 0
    for s in sources:
        enabled = cfg["sources"].get(f"{s}_enabled", "true") == "true"
        if not enabled:
            per_source[s] = {"enabled": False, "queries": 0}
            continue
        budget = int(cfg["sources"].get(f"{s}_budget", 60))
        queries = build_queries(cfg, s, terms, cursors.get(s))[:budget]
        per_source[s] = {"enabled": True, "queries": len(queries)}
        total += len(queries)
    return {"terms": len(terms), "cap": cap, "total": total,
            "per_source": per_source}


def request_cancel(cfg, job_id):
    """Flag a running hunt for cancellation. Returns True on success."""
    job = _read_job(cfg, job_id)
    if not job or job.get("status") != "running":
        return False
    _cancel_path(cfg, job_id).touch()
    job["cancel_requested"] = True
    _write_job(cfg, job)
    return True


def _cancel_path(cfg, job_id):
    # Sidecar file, separate from the job JSON. The progress writer
    # rewrites the JSON every query; a flag inside it would race.
    return state_path(cfg, "jobs", f"{job_id}.cancel")


def _refresh_cancel(cfg, job):
    # The sidecar file is the source of truth. Mirror it into the
    # job record so the UI can see the flag.
    flag = _cancel_path(cfg, job["job_id"]).exists()
    job["cancel_requested"] = flag
    return flag
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError, OverflowError):
        return False


def _claim_lock(cfg, job_id):
    # Refuse when another hunt holds a live lock. Stale locks are
    # marked abandoned so one dead run cannot block the human.
    jobs_dir = state_path(cfg, "jobs")
    for p in sorted(jobs_dir.glob("hunt-*.json")):
        try:
            job = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if job.get("status") != "running":
            continue
        pid = None
        pidfile = jobs_dir / (p.stem + ".pid")
        try:
            pid = int(pidfile.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            pid = None
        if pid and _pid_alive(pid):
            raise HuntRefused(
                f"hunt {job['job_id']} is already running (pid {pid}); "
                "stop it before starting another")
        job["status"] = "abandoned"
        job["finished_utc"] = _now()
        _write_job(cfg, job)
    (jobs_dir / f"{job_id}.pid").write_text(str(os.getpid()),
                                            encoding="utf-8")


def _release_lock(cfg, job_id):
    try:
        (state_path(cfg, "jobs") / f"{job_id}.pid").unlink()
    except OSError:
        pass


def run_hunt(cfg, target, sources, cap, started_by, mock=False):
    """Run one discrete hunt job. Returns the finished job record.

    The job file at state/jobs/<job_id>.json carries live progress.
    The loop checks safety.paused and cancel_requested between queries.
    """
    for s in sources:
        if s not in SOURCE_NAMES:
            raise ValueError(f"unknown source: {s}")
    max_terms = int(cfg["sources"].get("max_terms_per_sweep", 200))
    if cap > max_terms:
        raise HuntRefused(
            f"cap {cap} exceeds max_terms_per_sweep {max_terms}; refusing")
    job_id = ("hunt-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
              + "-" + secrets.token_hex(2))
    est = estimate_hunt(cfg, target, sources, cap)
    job = {
        "job_id": job_id, "target": target, "sources": list(sources),
        "cap": cap, "started_by": started_by, "started_utc": _now(),
        "status": "running", "mock": mock,
        "estimated_queries": est["total"],
        "cancel_requested": False,
        "per_source": {},
        "finished_utc": None,
    }
    for s in sources:
        info = est["per_source"][s]
        job["per_source"][s] = {
            "done": 0, "total": info["queries"], "hits": 0,
            "throttled": 0, "errors": 0,
            "status": "pending" if info["enabled"] else "disabled",
        }
    _write_job(cfg, job)

    if _paused(cfg):
        job["status"] = "paused"
        job["finished_utc"] = _now()
        _write_job(cfg, job)
        return job

    try:
        _claim_lock(cfg, job_id)
    except HuntRefused:
        job["status"] = "error"
        job["error"] = "another hunt is running"
        job["finished_utc"] = _now()
        _write_job(cfg, job)
        raise

    cursors = _load_cursors(cfg)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    hits_path = state_path(cfg, "hits", f"{today}.jsonl")
    queries_path = state_path(cfg, "queries", f"{today}.jsonl")
    terms = select_terms(cfg, target, cap)
    try:
        with hits_path.open("a", encoding="utf-8") as hf, \
             queries_path.open("a", encoding="utf-8") as qf:
            for s in sources:
                if _paused(cfg):
                    job["status"] = "paused"
                    break
                if _refresh_cancel(cfg, job):
                    job["status"] = "cancelled"
                    _write_job(cfg, job)
                    break
                ps = job["per_source"][s]
                if ps["status"] == "disabled":
                    continue
                ps["status"] = "running"
                budget = int(cfg["sources"].get(f"{s}_budget", 60))
                queries = build_queries(cfg, s, terms,
                                        cursors.get(s))[:budget]
                ps["total"] = len(queries)
                throttled_stop = False
                for q in queries:
                    if _paused(cfg):
                        job["status"] = "paused"
                        break
                    if _refresh_cancel(cfg, job):
                        job["status"] = "cancelled"
                        break
                    outcome, status, hits = fetch_query(cfg, s, q, mock=mock)
                    for h in hits:
                        h["job_id"] = job_id
                        hf.write(json.dumps(h) + "\n")
                    qf.write(json.dumps({
                        "ts": _now(), "job_id": job_id, "source": s,
                        "query_id": q["id"], "http_status": status,
                        "outcome": outcome, "hits": len(hits),
                    }) + "\n")
                    hf.flush()
                    qf.flush()
                    ps["done"] += 1
                    ps["hits"] += len(hits)
                    if outcome == "throttled":
                        ps["throttled"] += 1
                        throttled_stop = True
                        break  # Stop this source; the venue told us to stop.
                    if outcome == "error":
                        ps["errors"] += 1
                    _write_job(cfg, job)
                if job["status"] in ("paused", "cancelled"):
                    break
                if throttled_stop:
                    ps["status"] = "throttled"
                else:
                    ps["status"] = "done"
                    cursors[s] = job["started_utc"]
                _write_job(cfg, job)
        if job["status"] == "running":
            job["status"] = "done"
    finally:
        _release_lock(cfg, job_id)
        try:
            _cancel_path(cfg, job_id).unlink()
        except OSError:
            pass
    job["finished_utc"] = _now()
    _save_cursors(cfg, cursors)
    _write_job(cfg, job)
    return job


def resweep(cfg, sources):
    """Reset per-source since cursors. Manual re-sweep only."""
    cursors = _load_cursors(cfg)
    for s in sources:
        if s in SOURCE_NAMES:
            cursors.pop(s, None)
    _save_cursors(cfg, cursors)
    return sorted(s for s in sources if s in SOURCE_NAMES)
