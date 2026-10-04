# TODO: Recursive Sub-Hunts, Hunter OSINT Sources, Interactive Session Hunts & Session Attach

Work queue for [PLAN.md](PLAN.md). Delete a task line when it is done and verified.

## Handoff rules

- Read [MODULE.md](MODULE.md) Sections 2 and 3 before changing code.
- Work top to bottom. Each phase depends on the phases above it.
- Run `make test` after each phase. Do not start the next phase while tests fail.
- Record a partial task under "In progress" with the exact file and step.
- Do not put files in `plugins/swarm-forensics/` unless they ship with the plugin. `make install` copies that folder.

## In progress

None. All phases completed.

## Operator decisions

- 2026-10-04: Approved recursive sub-hunts (3 deep by default, configurable via `hunt.max_depth`).
- 2026-10-04: Approved searching other swarm hunter sites/blogs for indicators and datasets.
- 2026-10-04: Approved `/swarm-forensics attach <session_id|hunt_id>` to attach sessions to running hunters.
- 2026-10-04: Approved running `/swarm-forensics start` in a session with conversational guidance.
- 2026-10-04: Approved full database reset and scratch restart in Settings UI and `/swarm-forensics reset --force`.
- 2026-10-04: Approved live URL stream with one-click artifact capture and UI text selection.

## Completed Tasks

- Phase 1: Storage Layer (Schema v4 & Migrations). Added `parent_hunt_id`, `depth`, `session_id` to `hunts`, `.v3.bak` backup, settings, store tests.
- Phase 2: Multi-Worker Hunt Service & Recursive Sub-Hunts. Concurrent workers up to `hunt.max_active_hunts`, `spawn_subhunt()`, auto-spawning in `research.py`, cascading stops.
- Phase 3: Hunter OSINT Sources & Dataset Ingestion. `crt.sh`, `export.arxiv.org`, search templates for threat blogs, repos, research datasets.
- Phase 4: Interactive Session Hunts, Attach Verb & Session Tools. `/swarm-forensics attach`, session-bound `start`, `sf_spawn_subhunt`, `sf_attach_hunt` native tools.
- Phase 5: REST API & Desktop UI Tree View. `POST /hunts/{id}/spawn`, `GET /hunts/{id}/children`, depth badges, `+ Sub-hunt` spawner, attach command helper, 30 JS render tests.
- Phase 6: Documentation, Lint & Definition of Done. Updated `MODULE.md` (Sections 1-5, max 3 in Section 5), `README.md`, `SKILL.md`, `make test`, `make lint`, `make check` all 100% clean.
- Phase 7: Data Reset, Live URL Artifacts, UI Selection & ASD-STE100 Spec. Added Danger Zone reset (`/reset`, CLI `--force`), live URL feed with `+ Artifact` buttons, `userSelect: 'text'`, Architecture Mermaid diagram in `README.md`, detailed `SPEC.md` in ASD-STE100, and complete subcommands help.
