# Module: Hermes Tracehound Plugin

## 1. Intent & Scope
Build a Hermes-agent skill (`tracehound`) that recreates the swarm-forensics hunt methodology as a continuously running extension: periodic IOC scans across public sources (urlquery, Wayback CDX, arquivo.pt), dynamic IOC list management, pattern-based candidate-URL prediction, and a research job that watches what others publish and extracts new IOCs. Scope is agents, agent systems, and public evidence only. No human or operator attribution. No credentialed sources. Read-only public web.

## 2. Active Invariants
- The seed IOC set (`pug-research/detection/wordlist.txt`, `RULES.md`) is read-only. The plugin maintains its own working copy under `skills/tracehound/state/` (untracked).
- IOC terms are never deleted, only demoted to inactive with provenance, timestamp, and reason.
- Every scan hit MUST record source, query, term, timestamp, and evidence excerpt. Hits without provenance are not hits.
- All intervals MUST be configurable. No hardcoded schedule survives code review.
- Network access is curl-via-subprocess only (the VM's Python HTTP stack cannot parse the egress proxy env; see `~/TOOLS.md`). No new dependencies without written justification.
- Stdlib only: `argparse`, `configparser`, `json`, `re`, `subprocess`, `urllib.parse`.

## 3. Interfaces & Dependencies
- Hermes extension point: **skill** installed at `~/.hermes/skills/hunt/tracehound` (NousResearch hermes-agent). Manifest is `skills/tracehound/SKILL.md` (frontmatter: name, version, description, argument-hint, allowed-tools, homepage, repository, author, license, user-invocable).
- Dual invocation: model-invoked (`/tracehound <job>`) and headless via host cron calling `python3 scripts/tracehound.py --job <scan|update-iocs|predict-urls|research> [--config ...]`.
- `scripts/tracehound.py`: CLI dispatcher. Contract: every job reads `config.ini`, writes JSONL to `state/`, exits 0 on success with a one-line summary on stdout.
- `scripts/lib/config.py`: `load_config(path)` → dict. `scripts/lib/sources.py`: `fetch_urlquery()`, `fetch_cdx()`, `fetch_arquivo()` (curl subprocess, rate-limited). `scripts/lib/iocs.py`: `load_working_copy()`, `propose_term()`, `set_status()`. `scripts/lib/predict.py`: `generate_candidates(grammar)` → URL list. `scripts/lib/research.py`: `check_watchlist()` → candidate terms with provenance.
- Commands: run through the lane `Makefile` (`make help`). Targets: `check` (syntax + structure validation).
- Learning-loop dynamics (promotion thresholds, novelty scoring, feedback) live in `LEARNING.md`, owned separately. This module owns the machinery, not the policy.

## 4. Current State & Known Gaps
- State: Scaffold only. SKILL.md, config schema, and job CLIs exist. No live scan has run.
- State: Query templates in `references/query-templates.md` are derived from `pug-research/detection/RULES.md` (UQ-1..UQ-5, CDX-1..CDX-4).
- Gap: No native Hermes scheduler was found in the surveyed material; periodic execution assumes host cron. If hermes-agent documents hooks/scheduling, migrate the cron wrapper.
- Gap: `hermes skills install` scanner verdict for this skill is unverified. Network-access patterns may flag; the `git clone` + `cp`/`ln -s` path is the documented fallback.
- Gap: The research job's watchlist (Transluce, vendor feeds) is a stub list. Real feed URLs need curation.
- Gap: URL predictor templates are hand-derived from the current request grammar. They do not yet read `pug-research/grammar-network/request_grammar.json` directly.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Subagent]: Build on the Hermes **skill** extension point (`~/.hermes/skills/` + SKILL.md), not commands or hooks: skills are the documented, installable unit with a real manifest format.
- [2026-10-04 Subagent]: Schedule via host cron calling the script headless. No Hermes-native scheduler was found in the surveyed sources; do not invent one.
- [2026-10-04 Subagent]: Keep the seed IOC set read-only and the working copy untracked under `state/`. Provenance is append-only; demotion replaces deletion.
