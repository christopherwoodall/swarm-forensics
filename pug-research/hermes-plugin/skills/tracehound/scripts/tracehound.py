"""Tracehound: human-triggered agent-trace hunts for Hermes.

The human starts each hunt, watches progress in the job file, and can
cancel it. The human reviews every hit. No command here schedules
future work; there is no background path. Stdlib only.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from config import load_config, ensure_state, state_path  # noqa: E402


def cmd_hunt(cfg, args):
    from sources import run_hunt, estimate_hunt, resweep, HuntRefused
    raw_sources = (args.sources if args.sources
                   else cfg.get("hunt", {}).get("default_sources",
                                                "urlquery,cdx,arquivo"))
    sources = [s.strip().lower() for s in raw_sources.split(",") if s.strip()]
    max_terms = int(cfg["sources"].get("max_terms_per_sweep", 200))
    default_cap = int(cfg.get("hunt", {}).get("default_cap", 200))
    if args.cap is not None:
        cap = args.cap
    elif default_cap > 0:
        cap = default_cap
    else:
        cap = max_terms
    if args.resweep:
        reset = resweep(cfg, sources)
        print(f"hunt: cursors reset for: {', '.join(reset)}")
    try:
        est = estimate_hunt(cfg, target=args.target, sources=sources, cap=cap)
    except (ValueError, HuntRefused) as e:
        print(f"hunt: refused: {e}", file=sys.stderr)
        return 2
    print(f"hunt: plan: {est['terms']} terms, "
          f"{est['total']} queries across {len(sources)} source(s)")
    for s, info in est["per_source"].items():
        state = "on" if info["enabled"] else "off"
        print(f"hunt:   {s}: {info['queries']} queries ({state})")
    try:
        job = run_hunt(cfg, target=args.target, sources=sources, cap=cap,
                       started_by=args.started_by, mock=args.mock)
    except HuntRefused as e:
        print(f"hunt: refused: {e}", file=sys.stderr)
        return 2
    print(f"hunt: job {job['job_id']} finished with status {job['status']}")
    hits = sum(p["hits"] for p in job["per_source"].values())
    print(f"hunt: {hits} hits, "
          f"{sum(p['throttled'] for p in job['per_source'].values())} throttled, "
          f"{sum(p['errors'] for p in job['per_source'].values())} errors")
    print(f"hunt: job_id={job['job_id']}")
    return 0


def _active_job(cfg):
    jobs_dir = state_path(cfg, "jobs")
    if not jobs_dir.exists():
        return None
    cands = []
    for p in jobs_dir.glob("hunt-*.json"):
        try:
            job = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if job.get("status") == "running":
            cands.append(job)
    if not cands:
        return None
    return sorted(cands, key=lambda j: j.get("started_utc", ""))[-1]


def cmd_stop(cfg, args):
    from sources import request_cancel
    if args.job_id:
        p = state_path(cfg, "jobs", f"{args.job_id}.json")
        if not p.exists():
            print(f"stop: no such job: {args.job_id}", file=sys.stderr)
            return 2
        job_id = args.job_id
    else:
        job = _active_job(cfg)
        if not job:
            print("stop: no running hunt")
            return 0
        job_id = job["job_id"]
    if request_cancel(cfg, job_id):
        print(f"stop: cancel requested for {job_id}; "
              "the hunt stops after its current query")
        return 0
    print(f"stop: job {job_id} is not running", file=sys.stderr)
    return 2


def cmd_modify(cfg, args):
    from settings import set_setting, SettingsError
    try:
        stored = set_setting(cfg, args.setting, args.value)
    except SettingsError as e:
        print(f"modify: rejected: {e}", file=sys.stderr)
        return 2
    print(f"modify: ok: {args.setting} = {stored}")
    return 0


def cmd_status(cfg, args):
    from iocs import _load as _load_iocs, pending_entries
    jobs_dir = state_path(cfg, "jobs")
    jobs = []
    if jobs_dir.exists():
        for p in sorted(jobs_dir.glob("hunt-*.json"), reverse=True)[:10]:
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            jobs.append({
                "job_id": j["job_id"], "status": j["status"],
                "target": j.get("target"), "started_utc": j.get("started_utc"),
                "finished_utc": j.get("finished_utc"),
                "per_source": j.get("per_source", {}),
            })
    counts = {"active": 0, "proposed": 0, "inactive": 0, "quarantined": 0}
    try:
        for r in _load_iocs(cfg):
            if r["status"] in counts:
                counts[r["status"]] += 1
    except (OSError, json.JSONDecodeError):
        pass
    last = next((j for j in jobs if j["status"] in
                 ("done", "paused", "cancelled", "error", "abandoned")), None)
    summary = {
        "paused": cfg.get("safety", {}).get("paused", "false") == "true",
        "active_job": next((j["job_id"] for j in jobs
                            if j["status"] == "running"), None),
        "recent_jobs": jobs,
        "ioc_counts": counts,
        "review_pending": len(pending_entries(cfg)),
        "last_hunt": last,
    }
    print(json.dumps(summary, indent=1))
    return 0


def cmd_review(cfg, args):
    # Decision functions live in iocs.py (review-queue owner's module).
    # The human verdict and rationale are recorded on the entry.
    from iocs import accept_term, reject_term, narrow_term
    if not args.rationale:
        print("review: rejected: --rationale is required "
              "(decisions are audited)", file=sys.stderr)
        return 2
    try:
        if args.verdict == "accept":
            entry = accept_term(cfg, args.id, args.reviewer, args.rationale)
            print(f"review: {args.id} accepted -> active "
                  f"(term: {entry.get('term')})")
        elif args.verdict == "reject":
            entry = reject_term(cfg, args.id, args.reviewer, args.rationale)
            print(f"review: {args.id} rejected -> inactive "
                  f"(term: {entry.get('term')})")
        else:
            if not args.chunk:
                print("review: rejected: narrow REQUIRES --chunk",
                      file=sys.stderr)
                return 2
            new_id = narrow_term(cfg, args.id, args.chunk.strip(),
                                 args.reviewer, args.rationale)
            print(f"review: {args.id} narrowed; new pending entry {new_id} "
                  f"for chunk {args.chunk.strip()!r}")
    except ValueError as e:
        print(f"review: rejected: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_update_iocs(cfg, args):
    from iocs import update_from_hits
    n = update_from_hits(cfg)
    print(f"update-iocs: {n} terms proposed")
    return 0


def cmd_predict_urls(cfg, args):
    from predict import generate_candidates
    n = generate_candidates(cfg)
    print(f"predict-urls: {n} candidates generated")
    return 0


def cmd_research(cfg, args):
    from research import check_watchlist
    n = check_watchlist(cfg)
    print(f"research: {n} candidate terms proposed")
    return 0


def cmd_diagnose(cfg, args):
    import shutil
    import subprocess
    problems = []
    if not shutil.which("curl"):
        problems.append("curl not found on PATH")
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "--max-time", "15", "https://urlquery.net/"],
            capture_output=True, text=True, timeout=30)
        if r.stdout.strip() != "200":
            problems.append(f"urlquery.net returned HTTP {r.stdout.strip()}")
    except Exception as e:  # noqa: BLE001
        problems.append(f"urlquery.net unreachable: {e}")
    if problems:
        print("diagnose: PROBLEMS")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("diagnose: ok (curl present, urlquery.net reachable)")
    return 0


def main():
    ap = argparse.ArgumentParser(
        prog="tracehound",
        description="Tracehound: human-triggered agent-trace hunts. "
                    "Every scan is a discrete job the human starts, watches, "
                    "and can cancel. Nothing here runs on its own.")
    ap.add_argument("--config", default=None,
                    help="Path to config.ini (default: config.ini next to SKILL.md).")
    ap.add_argument("--state-dir", default=None,
                    help="Override [paths] state_dir.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("hunt", help="Start a discrete hunt job.")
    p.add_argument("--target", default="all",
                   help="Term filter: 'all' or a substring to match.")
    p.add_argument("--sources", default=None,
                   help="Comma list: urlquery,cdx,arquivo "
                        "(default: hunt.default_sources).")
    p.add_argument("--cap", type=int, default=None,
                   help="Max terms to sweep (default: hunt.default_cap; "
                        "0 means max_terms_per_sweep).")
    p.add_argument("--resweep", action="store_true",
                   help="Reset per-source since cursors before hunting.")
    p.add_argument("--mock", action="store_true",
                   help="Dry run: synthetic hits, no network.")
    p.add_argument("--started-by", default="cli",
                   help="Who started it: cli, console, palette.")
    p.set_defaults(func=cmd_hunt)

    p = sub.add_parser("stop", help="Cancel the running hunt (kill switch).")
    p.add_argument("--job-id", default=None,
                   help="Job to cancel (default: the active one).")
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("modify", help="Change one setting (validated).")
    p.add_argument("setting", help="Setting key, e.g. sources.request_delay_seconds.")
    p.add_argument("value", help="New value.")
    p.set_defaults(func=cmd_modify)

    p = sub.add_parser("status", help="JSON summary: jobs, IOCs, pause state.")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("review",
                       help="Decide a pending review-queue entry.")
    p.add_argument("verdict", choices=["accept", "reject", "narrow"])
    p.add_argument("id", help="Review entry id.")
    p.add_argument("--chunk", default=None,
                   help="Narrower term (required for narrow).")
    p.add_argument("--rationale", default="",
                   help="Reason for the decision (required, audited).")
    p.add_argument("--reviewer", default="human",
                   help="Who decided (recorded on the entry).")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("update-iocs",
                       help="Propose novel terms from recent hits (manual).")
    p.set_defaults(func=cmd_update_iocs)

    p = sub.add_parser("predict-urls",
                       help="Generate candidate URLs from observed grammar (manual).")
    p.set_defaults(func=cmd_predict_urls)

    p = sub.add_parser("research",
                       help="Check the research watchlist once (manual).")
    p.set_defaults(func=cmd_research)

    p = sub.add_parser("diagnose", help="Check curl and source reachability.")
    p.set_defaults(func=cmd_diagnose)

    # Worker-5 case management. Additive block: the parsers above are
    # untouched. `case` backs the `/swarm-forensics case ...` grammar.
    case = sub.add_parser("case", help="Case management: entities and links.")
    csub = case.add_subparsers(dest="case_cmd", required=True)

    p = csub.add_parser("add", help="Add an entity.")
    p.add_argument("type", choices=["trace", "agent", "swarm", "collection"])
    p.add_argument("label", help="Entity label.")
    p.add_argument("--text", default=None,
                   help="Trace text (trace only; runs indicator extraction).")
    p.add_argument("--job", default=None,
                   help="Hunt job id to link (trace only; stored in data_json).")
    p.add_argument("--provenance", default="",
                   help="Provenance string.")
    p.set_defaults(func=cmd_case_add)

    p = csub.add_parser("link", help="Link two entities.")
    p.add_argument("from_id", help="Source entity id.")
    p.add_argument("to_id", help="Target entity id.")
    p.add_argument("rel", choices=["trace_of", "member_of", "part_of",
                                   "related"])
    p.set_defaults(func=cmd_case_link)

    p = csub.add_parser("list", help="List entities.")
    p.add_argument("--type", default=None,
                   choices=["trace", "agent", "swarm", "collection"],
                   help="Filter by entity type.")
    p.set_defaults(func=cmd_case_list)

    p = csub.add_parser("graph",
                        help="Print the graph-view deep link.")
    p.set_defaults(func=cmd_case_graph)

    args = ap.parse_args()
    cfg = load_config(args.config, state_dir=args.state_dir)
    ensure_state(cfg)
    return args.func(cfg, args)


# ---------------------------------------------------------------------------
# Worker-5: case subcommand group. Appended; the code above is untouched.
# ---------------------------------------------------------------------------

def _case_db(cfg):
    import cases
    return cases.connect(cfg=cfg)


def cmd_case_add(cfg, args):
    import cases
    db = _case_db(cfg)
    try:
        if args.type == "trace" and args.text:
            eid = cases.add_trace(db, args.label, args.text,
                                  provenance=args.provenance,
                                  job_id=args.job)
            n = len(cases.list_indicators(db, eid))
            print(f"case add: trace {eid} ({n} indicators extracted)")
        else:
            eid = cases.add_entity(db, args.type, args.label,
                                   provenance=args.provenance)
            print(f"case add: {args.type} {eid}")
    except ValueError as e:
        print(f"case add: rejected: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_case_link(cfg, args):
    import cases
    try:
        lid = cases.link(_case_db(cfg), args.from_id, args.to_id, args.rel)
    except ValueError as e:
        print(f"case link: rejected: {e}", file=sys.stderr)
        return 2
    print(f"case link: {lid} ({args.from_id} -[{args.rel}]-> {args.to_id})")
    return 0


def cmd_case_list(cfg, args):
    import cases
    try:
        ents = cases.list_entities(_case_db(cfg), args.type)
    except ValueError as e:
        print(f"case list: rejected: {e}", file=sys.stderr)
        return 2
    for e in ents:
        print(f"{e['id']}  {e['type']:<10}  {e['label']}")
    return 0


def cmd_case_graph(cfg, args):
    print("open /tracehound/graph in the desktop app")
    return 0


if __name__ == "__main__":
    sys.exit(main())
