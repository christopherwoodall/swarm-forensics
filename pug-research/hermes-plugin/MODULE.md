# Module: Hermes Swarm Forensics Plugin

## 1. Intent & Scope
Provide a Hermes desktop plugin (`swarm-forensics`) that runs an autonomous swarm hunt. An operator starts the hunt. Hermes then searches the public web for agent traces, mines new indicators, and writes events, evidence, IOCs, and an entity graph (agents, swarms, cases) to a local SQLite database. The hunt runs until the operator stops it. Scope is agents, agent systems, and public evidence. No operator attribution. No credentialed sources. Read-only public web.

## 2. Active Invariants
- A hunt starts only by an operator act: the desktop Start button, the `/swarm-forensics start` command, or a schedule the operator armed. Once started, the hunt runs autonomously until the operator stops it.
- Schedules are opt-in. `schedule.enabled` defaults to false and each schedule starts unarmed. Scheduled hunts run only while the desktop app sends heartbeats.
- A hunt MUST stop when the desktop heartbeat lapses (`hunt.require_desktop`). After a host restart, `recover()` sets a stale hunt to `paused`. Only an operator resumes it.
- The model proposes. Policy code and the operator decide. Model output MUST pass the strict parsers in `safety.py` before any write.
- Fetched text is untrusted data. It MUST be fenced in prompts. Evidence flagged as tainted MUST NOT support an IOC promotion.
- IOC promotion defaults to `manual`. `automatic` mode MUST enforce `iocs.auto_min_evidence`, `iocs.auto_min_sources`, `iocs.auto_min_claim_level`, and `iocs.auto_max_per_day`. Every status change MUST write an `ioc_log` row with actor, reason, and time.
- IOC terms are never deleted. They move to `inactive` or `rejected` with a reason.
- Every evidence row MUST record source, query, URL, excerpt, and observed time. Rows without provenance are not evidence.
- A throttled or failed query (HTTP 429/403/5xx) MUST be logged as throttled or failed, never as a negative.
- Index adapters MUST fetch only allowlisted hosts (`urlquery.net`, `web.archive.org`, `arquivo.pt`) through `curl`. Open-web search and page reads MUST go through Hermes tools.
- URLs and text MUST be redacted (`redact_url`, `redact_text`) before they reach the database.
- All SQL MUST be parameterized. The database is local-only and MUST NOT sync or export except by an explicit operator act.
- Hunt state lives outside the plugin directory (`<hermes home>/swarm-forensics/`). Plugin updates MUST NOT touch it. Schema changes use `PRAGMA user_version` migrations.
- Python dependencies: standard library for the engine. `fastapi` is used only in `dashboard/plugin_api.py` and comes from Hermes. The desktop file imports only `@hermes/plugin-sdk`, `react`, and `react/jsx-runtime`.

## 3. Interfaces & Dependencies
- Package: `plugins/swarm-forensics/` is one unified plugin. `plugin.yaml` and `__init__.py` (`register(ctx)`) form the agent half. `desktop/plugin.js` is the single ESM desktop file. `dashboard/manifest.json` and `dashboard/plugin_api.py` (`router`) form the backend. `skills/swarm-forensics/SKILL.md` is the agent guide.
- Engine: `swarm_forensics_plugin/` is shared by the agent half and the backend. Both add the plugin directory to `sys.path` and call `service.get_service()`, so one service exists per process.
- Modules: `db` (schema, migrations), `settings` (typed schema, validation), `safety` (URL checks, redaction, taint screen, fencing, strict parsers), `extract` (indicators), `entities` (graph, wikilinks), `iocs` (store, audited transitions, `apply_policy`), `ledger` (hunts, events, evidence, leads, cursors), `predict` (candidate URLs), `sources` (index adapters), `hermes` (`HermesRuntime`: `ctx.llm`, `dispatch_tool`), `prompts`, `research` (`Engine` cycle), `schedule` (interval and UTC cron), `hunt` (`HuntService`, worker, lease, scheduler), `legacy` (one-time import), `command` (`/swarm-forensics`).
- Backend routes (mounted at `/api/plugins/swarm-forensics`): `overview`, `heartbeat`, `status`, `hunts` (`start`, `stop`, `pause`, `resume`, list, one), `events`, `leads`, `evidence`, `iocs` (list, add, `decision`), `entities` (CRUD), `links`, `graph`, `extract-preview`, `settings`, `schedules` (`arm`).
- Hermes dependencies: `PluginContext.register_command`, `register_skill`, `ctx.llm`, `dispatch_tool` (`web_search`, `web_extract`). `broadcast_plugin_event` is optional and import-guarded. The backend needs Hermes with plugin dashboard support (tested with fastapi 0.133.1).
- Desktop element helper: `h(type, props, ...kids)` in `plugin.js` MUST omit `children` when there are none (void elements such as `<input>` reject it, React error #137). It MUST pass `key` as the third argument to `jsx`/`jsxs`.
- Test-only JS dependencies: `tests/package.json` declares `react` and `react-dom`. `make js-deps` installs them to `~/.cache/swarm-forensics-plugin/js`, outside the repository and outside the installed plugin.
- `/swarm-forensics` verbs: `start`, `stop`, `pause`, `resume`, `status`, `log [n]`, `review`, `accept`, `reject`, `narrow`, `find`, `settings`. A command handler returns one string, so a hunt MUST NOT be expected to post to the chat. Progress is pull-based: `log` and `status`, and the desktop Activity feed. The engine writes one event per step (`plan`, `search`, `sweep`, `page`, `cycle`).
- Commands (lane `Makefile`, also via root `hermes-*` targets): `test`, `lint`, `check`, `js-deps`, `install`, `uninstall`. `install` copies the package to the Hermes home and runs `hermes plugins enable`.

## 4. Current State & Known Gaps
- State: Rewrite complete (2026-10-04). 69 offline Python tests and 16 JS render tests pass (`tests/render.test.mjs`: every tab renders with data, loading, and offline states under a real React; any React console error fails the test). `make lint` and `make check` pass. `hermes plugins validate` passes (security scan safe, desktop surface inside the SDK). `hermes plugins doctor` passes. `make install` installed and enabled the plugin in the Windows desktop Hermes.
- State: The first-generation CLI, HTTP server, firewall judge, and old design documents are removed. Their content remains in git history. The importer reads old state once.
- Gap: No live hunt has run against real sources or a real model. Tests use scripted fakes and synthetic data.
- Gap: The desktop UI renders in server-side tests only. Click handlers, effects, graph pan/zoom, and palette commands have not run in the desktop app. Verify them by hand.
- Gap: `broadcast_plugin_event` is absent in the checked Hermes source. The app falls back to polling (20 s heartbeat, alert poll).
- Gap: Dashboard responses are buffered by the plugin host. Live progress uses polling, not streaming.
- Gap: The WSL `~/.hermes` install (v1.0.0, Feb 2026) has no plugin system. Install targets the Windows desktop Hermes unless `HERMES_HOME` is set.
- Gap: The `urlquery` adapter endpoint (`https://urlquery.net/api/v1/search`) returns HTTP 404 (checked 2026-10-04). Each failed sweep now writes a warn event. The correct API, and whether it needs a key, is unknown. The default `hunt.sources` still lists `urlquery`.
- Gap: `ctx.inject_message` can push text into a session, but it injects a user message, needs a `session_key` that command handlers do not get, and needs `allow_gateway_injection`. It is not used.
- Gap: No negotiated rate agreement with urlquery.net. The code throttles and backs off.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Droid]: Made hunt progress pull-based (`log` verb, per-step events) instead of injecting chat messages. Rationale: injection creates user turns that cost tokens and break Hermes message-alternation rules, and command handlers have no session key.
- [2026-10-04 Droid]: Fixed React error #137 by dropping empty `children` in `h()`, and added server-render tests with a real React. Rationale: syntax checks and the Hermes validator do not render pages, so a bad element tree reached the desktop app.
- [2026-10-04 Droid]: Replaced the human-only hunting-dog model with an operator-started autonomous hunter. The operator chose manual plus configurable automatic IOC promotion, opt-in schedules, and a resumable on-disk database. Rationale: deep research needs a continuous loop. Controls move from per-step approval to start/stop, policy limits, and audit logs.
