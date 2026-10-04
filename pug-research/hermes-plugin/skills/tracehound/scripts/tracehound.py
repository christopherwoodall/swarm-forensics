"""Tracehound: periodic agent-trace hunting for Hermes.

Dispatcher for the four jobs. Every job reads config.ini, writes JSONL
under state/, and exits 0 with a one-line summary on stdout.
Stdlib only.
"""

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from config import load_config, ensure_state  # noqa: E402


def cmd_scan(cfg, args):
    from sources import run_scan
    n = run_scan(cfg)
    print(f"scan: {n} new hits")
    return 0


def cmd_update_iocs(cfg, args):
    from iocs import update_from_hits
    n = update_from_hits(cfg)
    print(f"update-iocs: {n} terms proposed/promoted/demoted")
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


JOBS = {
    "scan": cmd_scan,
    "update-iocs": cmd_update_iocs,
    "predict-urls": cmd_predict_urls,
    "research": cmd_research,
    "diagnose": cmd_diagnose,
}


def main():
    ap = argparse.ArgumentParser(description="Tracehound job dispatcher.")
    ap.add_argument("--job", required=True, choices=sorted(JOBS),
                    help="Job to run.")
    ap.add_argument("--config", default=None,
                    help="Path to config.ini (default: config.ini next to SKILL.md).")
    ap.add_argument("--state-dir", default=None,
                    help="Override [paths] state_dir.")
    args = ap.parse_args()
    cfg = load_config(args.config, state_dir=args.state_dir)
    ensure_state(cfg)
    return JOBS[args.job](cfg, args)


if __name__ == "__main__":
    sys.exit(main())
