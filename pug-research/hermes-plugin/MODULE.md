# Module: Hermes Swarm Forensics Plugin

## 1. Intent & Scope
Provide a Hermes desktop plugin (`swarm-forensics`) that runs autonomous and interactive swarm hunts. Operators can run hunts through the desktop plugin, chat commands, or interactive Hermes chat sessions. Hermes searches the public web for agent traces. It writes events, evidence, IOCs, URLs, prompts, and an entity graph to SQLite. Scope covers agents, swarms, campaigns, artifacts, and public evidence. No credentialed sources. Read-only public web.

## 2. Active Invariants
- A hunt starts only by an operator act: desktop Start button, `/swarm-forensics start`, or an armed schedule.
- An interactive hunt runs as a standard Hermes session with native `sf_*` tools.
- A hunt MAY spawn child sub-hunts up to `hunt.max_depth` (default 3).
- Stopping a parent hunt MUST stop all active child hunts.
- Operators MAY attach any chat session to running hunts with `/swarm-forensics attach`.
- Schedules are opt-in. `schedule.enabled` defaults to false. Scheduled hunts run only with desktop heartbeats.
- A background hunt MUST stop when the desktop heartbeat lapses (`hunt.require_desktop`).
- The model proposes. Policy code and the operator decide. Model output MUST pass safety parsers.
- Fetched text is untrusted data. It MUST be fenced in prompts. Tainted evidence MUST NOT support IOC promotion.
- IOC promotion defaults to `manual`. Items marked `benign` MUST NOT be promoted.
- Items marked `benign` act as negative filters. The engine MUST NOT search or probe benign URLs or terms.
- Prompts live in SQLite. Operators MAY edit templates. Resetting a prompt restores its immutable default template.
- IOC terms are never deleted. They move to `inactive`, `rejected`, or `benign` with an audit reason.
- Every evidence row MUST record source, query, URL, excerpt, and observed time.
- Throttled or failed queries (HTTP 429/403/5xx) MUST be logged as throttled or failed, never as negative.
- Index adapters MUST fetch only enabled index sources in the database through `curl`.
- Entities MUST conform to the hierarchy `artifact -> agent -> swarm -> campaign`, or unranked `collection`.
- URLs and text MUST be redacted before write.
- All SQL MUST be parameterized. Hunt state lives in `<hermes home>/swarm-forensics/`.
- Python engine dependencies MUST remain standard library only. Desktop JS MUST use pure ESM.

## 3. Interfaces & Dependencies
- Package: `plugins/swarm-forensics/` is one unified plugin. `register(ctx)` registers commands, tools, and skills.
- Modules: `db` (schema v4), `settings`, `safety`, `extract`, `entities`, `prompt_registry`, `url_store`, `agent_tools`, `registry`, `export`, `iocs`, `ledger`, `predict`, `sources`, `hermes`, `prompts`, `research`, `schedule`, `hunt`, `command`.
- Backend routes: `overview`, `heartbeat`, `status`, `hunts` (start, stop, pause, resume, spawn, children), `events`, `leads`, `evidence`, `iocs`, `urls` (list, triage), `prompts` (CRUD, reset, export, import), `entities` (CRUD, group, tag), `links`, `graph`, `sources`, `grammar`, `export`, `settings`, `schedules`.
- Hermes agent tools: `sf_get_context`, `sf_search_index`, `sf_record_evidence`, `sf_propose_ioc`, `sf_manage_entity`, `sf_link_entities`, `sf_triage_item`, `sf_query_knowledge`, `sf_spawn_subhunt`, `sf_attach_hunt`.
- Desktop UI: Hunt (activity, leads, session commands, sub-hunt tree, attach), Knowledge (graph, hierarchy, custom groups, tags), Evidence, IOCs (benign triage), URLs (catalog, benign filter), Prompts (templates, token chips, reset, import/export), Sources, Settings.
- `/swarm-forensics` verbs: `start`, `stop`, `pause`, `resume`, `attach`, `status`, `log`, `review`, `accept`, `reject`, `benign`, `session`, `narrow`, `find`, `settings`.
- Commands: `test`, `lint`, `check`, `js-deps`, `install`, `uninstall`.

## 4. Current State & Known Gaps
- State: Schema v4, multi-worker recursive sub-hunts, hunter OSINT sources, session attach, and tree UI complete (2026-10-04).
- State: 120 offline Python unit tests and 30 JS render tests pass.
- State: `make lint` and `make check` pass with zero errors.
- Gap: No live hunt has run against real external sources. Tests use fakes and synthetic data.
- Gap: Desktop UI click handlers run in server render tests only. Operators SHOULD verify interactive behavior in the Hermes desktop app.
- Gap: `broadcast_plugin_event` is optional. The desktop app uses polling fallbacks.
- Gap: The `urlquery` adapter endpoint returns HTTP 404 and remains disabled by default.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Antigravity]: Added Schema v4, multi-worker recursive sub-hunts (max depth 3), OSINT sources (crt.sh, arXiv), session attach, and tree UI. Rationale: Operator requested crawling child hunts, research blog discovery, and interactive session attachment.
- [2026-10-04 Antigravity]: Upgraded schema to v3 with DB prompts, URL catalog, benign triage, custom swarms, and Hermes session tools. Rationale: Operator requested interactive chat hunts, editable prompts, and database workbench control.
- [2026-10-04 Antigravity]: Migrated schema to v2, enforced strict entity hierarchy, and added index source registry and export vault. Rationale: Operator approved dynamic source allowlist, directional hierarchy, and offline Obsidian vault export.

