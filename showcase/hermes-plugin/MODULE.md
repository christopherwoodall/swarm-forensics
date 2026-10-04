# Module: Hermes Swarm Forensics Plugin

## 1. Intent & Scope
Provide a Hermes desktop plugin (`swarm-forensics`) that runs autonomous and interactive swarm hunts. Operators can run hunts through the desktop plugin, chat commands, or interactive Hermes chat sessions. Hermes searches the public web for agent traces. It writes events, evidence, IOCs, URLs, prompts, and an entity graph to SQLite. Scope covers agents, swarms, campaigns, artifacts, and public evidence. No credentialed sources. Read-only public web.

## 2. Active Invariants
- A hunt starts only by an operator act: desktop Start button, `/swarm-forensics start`, or an armed schedule.
- Multiple hunts MAY run concurrently up to `hunt.max_active_hunts` (default 3). Each chat session follows its own bound hunt.
- A hunt runs in either session mode (native chat agent) or background mode (scheduled or headless worker threads).
- Session hunts MUST bind real durable Hermes session identifiers.
- Session identity MUST be read through `session_env` (ContextVar-aware), never bare `os.getenv` on host worker threads.
- Chat narration MUST go through `ctx.inject_message` with the durable session key and MUST respect the host's `allow_gateway_injection` consent. Denial sets `narration_blocked`; it MUST NOT raise.
- Session-scoped verbs target the calling session's bound hunt. With no binding and several active hunts, verbs MUST ask for an id instead of guessing. `on_session_start` MUST NOT auto-bind when zero or several unbound hunts are active.
- An interactive hunt runs as a standard Hermes session with native `sf_*` tools.
- A hunt MAY spawn child sub-hunts up to `hunt.max_depth` (default 3).
- Stopping a parent hunt MUST stop all active child hunts.
- Operators MAY attach any chat session to running hunts with `/swarm-forensics attach`.
- Schedules are opt-in. `schedule.enabled` defaults to false. Scheduled hunts run only with desktop heartbeats.
- A background hunt MUST stop when the desktop heartbeat lapses (`hunt.require_desktop`).
- The model proposes. Policy code and the operator decide. Model output MUST pass safety parsers.
- Raw-data discovery MUST require explicit authorization before exposing redacted excerpts to the configured model.
- Raw-data model prose MUST remain transient. Saved discovery cards and reports MUST contain only code-generated text, measurements, and provenance.
- Imported morphology candidates MUST remain hypotheses. Import MUST NOT start hunts or promote IOCs.
- Fetched text is untrusted data. It MUST be fenced in prompts. Tainted evidence MUST NOT support IOC promotion.
- Mirrored content MUST come from Hermes `web_extract`, MUST be text only, and MUST be fenced as untrusted.
- Tool observations in session hunts MUST be captured through plugin lifecycle hooks and correlated with the bound hunt.
- IOC promotion defaults to `manual`. Items marked `benign` MUST NOT be promoted.
- Items marked `benign` act as negative filters. The engine MUST NOT search or probe benign URLs or terms.
- Prompts live in SQLite. Operators MAY edit templates. Resetting a prompt restores its immutable default template.
- IOC terms are never deleted. They move to `inactive`, `rejected`, or `benign` with an audit reason.
- Operators MAY reset all data via `POST /reset` or `/swarm-forensics reset --force`.
- Data reset MUST terminate active workers, wipe custom tables, and restore seed defaults.
- Desktop pages MUST allow text selection and copying.
- Every evidence row MUST record source, query, URL, excerpt, and observed time.
- Throttled or failed queries (HTTP 429/403/5xx) MUST be logged as throttled or failed, never as negative.
- Index adapters MUST fetch only enabled index sources in the database through `curl`.
- Public index sources MUST declare authentication requirements. Keyed sources without credentials MUST be disabled with explicit reason.
- Entities MUST conform to the hierarchy `artifact -> agent -> swarm -> campaign`, or unranked `collection`.
- URLs and text MUST be redacted before write.
- All SQL MUST be parameterized. Hunt state lives in `<hermes home>/swarm-forensics/`.
- Python engine dependencies MUST remain standard library only. Desktop JS MUST use pure ESM.

## 3. Interfaces & Dependencies
- Package: `plugins/swarm-forensics/` is one unified plugin. `register(ctx)` registers commands, tools, hooks, and skills.
- Modules: Core modules include `db`, `settings`, `safety`, `extract`, `entities`, `prompt_registry`, `url_store`, and `mirror`. Engine modules include `agent_tools`, `registry`, `export`, `iocs`, `ledger`, `predict`, `sources`, `analysis`, `hooks`, `session_env`, `narration`, and `command`.
- Discovery modules: `dataset_probes` streams bounded records. `dataset_hunter` runs adaptive probes. `morphology` validates imported candidate cards.
- Backend routes: Routes serve hunts, events, leads, evidence, and IOCs. Other routes serve URLs, entities, mirrors, corpus, and settings.
- Morphology routes: `POST /morphologies/discover` returns measurements and transient interpretations. `POST /morphologies` imports a card. `GET /morphologies` lists metadata. Detail and review routes use `/morphologies/{record_id}`.
- Hermes agent tools: `sf_get_context`, `sf_get_morphology_candidates`, `sf_search_index`, `sf_record_evidence`, `sf_mirror_url`, `sf_analyze_corpus`, `sf_propose_ioc`, `sf_manage_entity`, `sf_link_entities`, `sf_triage_item`, `sf_query_knowledge`, `sf_spawn_subhunt`, `sf_attach_hunt`.
- Investigator retrieval: Field selectors MUST name required card fields. Full-card paging retains optional fields.
- Investigator retrieval: `sf_get_morphology_candidates` supports exact `field` selection and zero-based `page`. Follow `next_page` until `has_more` is false. Each fenced page contains at most 12,000 characters.
- Desktop UI: Pages include Hunt, Knowledge, Morphologies, Evidence, IOCs, URLs, Prompts, Sources, and Settings. Components include composer underside strip and companion pane. Slot and pane hosts mount contributions with no props. Components MUST read the focused session from `host.state.focusedSessionId` via `useValue`, preferring `focusedStoredSessionId` (durable) for backend lookups. Pane contributions MUST declare a top-level `title` and `data.placement`.
- Narration: `narration.py` posts batched digests and drive prompts into bound sessions. A fresh session hunt gets an immediate kickoff prompt; `narrate.drive_idle_seconds` gates only later stall nudges. Tuning lives in `narrate.enabled`, `narrate.min_interval_seconds`, and `narrate.drive_idle_seconds`. The installer writes `plugins.entries.swarm-forensics.allow_gateway_injection: true` via `hermes config set`.
- `/swarm-forensics` verbs: Control verbs include `start`, `attach`, `subhunt`, `tools`, `stop`, `pause`, and `resume`. Inspection verbs include `status`, `log`, `review`, `accept`, `reject`, `benign`, `narrow`, `find`, `settings`, and `reset`.
- Commands: `setup`, `lock`, `test`, `lint`, `check`, `js-deps`, `hunter`, `hunter-test`, `hunter-ui-test`, `install`, `uninstall`. Root Make targets delegate to this module. Development dependencies live in this module’s `pyproject.toml` and `uv.lock`.

## 4. Current State & Known Gaps
- State: Schema v6, session-native execution, and Hermes session bindings are complete.
- State: Local text mirror, TTP analysis, composer underside strip, and companion pane are complete.
- State: 189 offline Python unit tests and 39 JS render tests pass.
- State: Adaptive raw-data discovery, audited candidate intake, and measurement-only discovery persistence pass synthetic acceptance tests.
- State: Reset invalidates pending discovery persistence. Concurrent reviews preserve serialized audit transitions.
- State: CLI report destinations reject source aliases. Investigator paging preserves prepared content across page boundaries.
- State: Native card values are sanitized before serialization. Fencing preserves JSON syntax and short assignments.
- State: Chat narration (digests, drive prompts, denial flag) and multi-session hunts are complete.
- State: `make lint` and `make check` pass with zero errors.
- Gap: Discovery measures literal recurrence and recorded three-operation sequences, not causality or verified coordination.
- Gap: Sequence candidates are frequency-capped before null comparison. Joint support across observations remains unmeasured.
- Gap: Final-round probe requests can execute without another model feedback round.
- Gap: No live hunt has run against real external sources. Tests use fakes and synthetic data.
- Gap: Desktop tests cover server rendering and synthetic request handlers. Live Hermes desktop interaction remains unverified.
- Gap: `broadcast_plugin_event` is optional. The desktop app uses polling fallbacks.
- Gap: The `urlquery` adapter endpoint returns HTTP 404 and remains disabled by default.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Hermes]: Port the hunter onto the showcase layout. Preserve migrations 1–5 and append migration 6. Retain measurements-only discovery persistence. Sanitize dictionary keys and provide paged investigator retrieval. Serialize review transitions, invalidate discovery after reset, and refuse source-output collisions.
- [2026-10-04 Droid]: Replaced the single-root-hunt refusal with the `hunt.max_active_hunts` cap, added ContextVar-aware session identity (`session_env`), and added chat narration through `ctx.inject_message` with installer-written `allow_gateway_injection` consent. A target that fails 3 posts in a row is muted for 10 minutes so a stale binding cannot hold the global `narration_blocked` flag. Rationale: Chat hunts were invisible in their own sessions and only one hunt could run; live verification showed a dead binding poisoning the blocked flag.
- [2026-10-04 Droid]: Fixed strip and pane session resolution. Desktop Slot and pane hosts pass no props, so components read `host.state.focusedSessionId` via `useValue`. Pane registration gained top-level `title` and a namespaced id. Rationale: Strip and pane rendered without session context and the pane lacked a tab label.
