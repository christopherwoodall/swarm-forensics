# Module: Hermes Tracehound Plugin

## 1. Intent & Scope
Build a Hermes desktop-app plugin (`tracehound`) that implements the swarm-forensics hunt methodology as a human-operated hunting-dog console: the human starts every hunt, watches progress, triages every candidate, and approves every IOC promotion. The plugin points, flushes, and retrieves — the human decides what to shoot. Scope is agents, agent systems, and public evidence only. No human or operator attribution. No credentialed sources. Read-only public web. Private deployment only.

## 2. Active Invariants
- The seed IOC set (`pug-research/detection/wordlist.txt`, `RULES.md`) is read-only. The plugin maintains its own working copy under `skills/tracehound/state/` (untracked).
- IOC terms are never deleted, only demoted to inactive with provenance, timestamp, and reason.
- Every scan hit MUST record source, query, term, timestamp, and evidence excerpt. Hits without provenance are not hits.
- No autonomous execution: no scheduler, no cron, no background jobs. Every hunt is human-initiated from the desktop console or the `/swarm-forensics` command.
- No promotion without a human decision (GUI click or `review accept`). `auto_propose` defaults to false; proposals enter quarantine, never the active list.
- `firewall_mode` is `advisory` or `off`. `enforcing` is locked in code until the firewall passes the injection-resistance eval.
- A throttled query (HTTP 429/403) MUST be logged as throttled, never as a negative.
- Network access is curl-via-subprocess only (the VM's Python HTTP stack cannot parse the egress proxy env; see `~/TOOLS.md`). No new dependencies without written justification.
- Stdlib only: `argparse`, `configparser`, `json`, `re`, `subprocess`, `urllib.parse`.

## 3. Interfaces & Dependencies
- Delivery: unified Hermes desktop package. Agent/skill half at `skills/tracehound/` (manifest `SKILL.md`); desktop half at `skills/tracehound/desktop/plugin.js` (single hot-reloaded ESM file); Python backend at `skills/tracehound/dashboard/plugin_api.py`. Install: `hermes://plugin/install?repo=christopherwoodall/swarm-forensics&enable=1` (confirm-first; see HERMES_DESKTOP.md §2.8).
- Invocation (one threat model): the desktop GUI (routes `/tracehound`, `/tracehound/hunt`, `/chat`, `/review`, `/iocs`, `/research`, `/settings`) and the `/swarm-forensics` command grammar (`hunt`, `stop`, `modify`, `status`, `review …`) are two faces of the same state. Both call the backend; the backend enforces allowlisted hosts, per-source budgets, check-don't-fetch, and the paused state.
- `scripts/tracehound.py`: CLI dispatcher and the command backing. Subcommands: `hunt`, `stop`, `modify`, `status`, `review`, `update-iocs`, `predict-urls`, `research`, `diagnose`. Contract: every job reads `config.ini`, writes JSONL under `state/`, exits 0 with a one-line summary on stdout. Nothing schedules future work.
- `scripts/lib/`: `config.py` (load/validate), `settings.py` (typed get/set with the `firewall_mode` lock), `sources.py` (`run_hunt`, `estimate_hunt`, `request_cancel`; HTTP-status handling), `iocs.py` (working copy, review queue `state/review.json`, human decision functions), `firewall.py` (advisory-only harness, taint pre-screen, golden set), `predict.py` (grammar-driven candidates), `research.py` (watchlist → quarantine).
- `dashboard/plugin_api.py`: REST namespace — `GET /hits /iocs /review /candidates /jobs /jobs/<id> /settings /diagnostics`; `POST /hunt/start /hunt/stop /review/decision /chat /settings/pause`; `PUT /settings`. Single enforcement point for GUI and command.
- Commands: run through the lane `Makefile` (`make help`). Targets: `check` (syntax + structure), `selftest` (firewall parser + taint screen, no model), `desktop-check` (node --check on `plugin.js` + backend py_compile).
- Learning-loop dynamics live in `LEARNING.md` (human-gated amendment, 2026-10-04). This module owns the machinery, not the policy.

## 4. Current State & Known Gaps
- State: Hunting-dog build complete in code (2026-10-04). Hunter core (3 sources, 429 handling, sweep caps, kill-switch, discrete jobs), human-gated IOC updater + review queue, advisory-only firewall harness, grammar-driven predictor, full desktop GUI + backend, `/swarm-forensics` grammar. No live hunt has run against real sources yet (mock only).
- State: Install link `hermes://plugin/install?repo=christopherwoodall/swarm-forensics&enable=1` documented with SDK citations (HERMES_DESKTOP.md §2.8). The plugin ships in a repo subdirectory; the installer's artifact probe behavior against a live app is unverified.
- State: Query templates in `references/query-templates.md` derived from `pug-research/detection/RULES.md`; predictor now reads `pug-research/grammar-network/request_grammar.json` programmatically.
- Gap: Prompt firewall has no judge endpoint configured (`enabled=false` default). The injection-resistance eval against `references/firewall-golden.jsonl` must pass before advisory mode enables.
- Gap: No negotiated rate agreement with urlquery.net. Code caps and backs off, but the human conversation is still required before routine use.
- Gap: Research watchlist is a stub list. Real feed URLs need curation.
- Gap: `hermes skills install` scanner verdict for this skill is unverified; the `hermes://` link path is now primary.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Coordinator]: Hunting-dog model — drop the autonomous hunter entirely; every hunt is human-triggered, the updater only proposes, the firewall stays advisory-only and locked. Rationale: the adversarial delta closed 10 of 12 objections under this model; the autonomous self-updating hunter was self-defeating (#1, #2) and abusive (#3).
- [2026-10-04 Coordinator]: The desktop app is the whole product — full GUI plus `/swarm-forensics` command as two faces of one state, with `dashboard/plugin_api.py` as the single enforcement point. Rationale: one threat model (#12); nothing runs while the app is closed (accepted).
- [2026-10-04 Coordinator]: Private deployment only — tripwire strings never ship in a public artifact. Rationale: publication destroys the zero-baseline tripwires the hunt depends on (#1, #11).
