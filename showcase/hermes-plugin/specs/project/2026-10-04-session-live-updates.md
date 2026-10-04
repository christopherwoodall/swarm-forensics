# Session Live Updates + Multi-Session Hunts

Date: 2026-10-04
Status: Approved

## Goal

Hunt activity MUST appear live inside the individual chat session window, not only in
the Swarm Forensics capabilities panel. The plugin MUST support more than one
concurrent hunt session.

Root causes established by read-only investigation of the live app and Hermes
internals:

1. Chat-origin hunts never bind to their session. Slash commands run on a worker
   thread where session identity is bound via ContextVar
   (`gateway/session_context.py::get_session_env`), not `os.environ`. The plugin
   read `os.getenv("HERMES_SESSION_ID")`, saw nothing, and created an unbound
   `origin=command` hunt (confirmed in the live DB, hunt `48e82be8...`).
2. Nothing wrote into the transcript. Narration events sit in the SQLite `events`
   table; no code called `ctx.inject_message()`, the only sanctioned bridge into a
   chat session (`hermes_cli/plugins.py:604`, routed via
   `tui_gateway/plugin_inject.py` keyed on the durable `session_key`).
3. The desktop strip/pane looked up the runtime session id while bindings store the
   durable key, so lookups missed even for attached hunts.
4. `HuntService.start()` hard-refused a second root hunt (`hunt.py`), blocking
   multi-session use even though `hunt.max_active_hunts` (default 3) and per-hunt
   workers already exist.

## Mechanism

### 1. Session identity fix

- `command.py` and `agent_tools.py` MUST read `HERMES_SESSION_ID` /
  `HERMES_SESSION_KEY` via `gateway.session_context.get_session_env` (guarded
  import; `get_session_env` itself falls back to `os.environ`). Chat-invoked
  `/swarm-forensics start` then creates `origin=session` hunts bound to the calling
  session's durable key.

### 2. Narrator

New module `swarm_forensics_plugin/narration.py`, owned by `HuntService` (which
holds the plugin `ctx`).

- Poll every ~5 seconds. For each active hunt with session bindings, collect new
  events since a per-hunt cursor (`narrate:<hunt_id>` in the cursors table).
- Digest (all bound hunts): a batched, throttled user message
  (`narrate.min_interval_seconds`, default 60) of the form
  `[swarm-forensics] hunt <id8> -- <state> cycle n/m` with bullets for search
  queries, tool calls, and findings, plus a one-line rationale from the latest
  planning brief. Cap ~1200 chars. Footer lists steering verbs.
- Drive (session-origin hunts only): when the hunt is active and no new events
  arrive for `narrate.drive_idle_seconds` (default 120), inject a continuation
  prompt with current leads so the native model keeps hunting. Stall guard: stop
  after 3 consecutive drives with no new events.
- Denial: when `inject_message` returns False, log once and set a
  `narration_blocked` flag exposed by `/status` and `/sessions/{id}/overview` so
  the UI can show the remediation hint.
- New settings: `narrate.enabled` (default true), `narrate.min_interval_seconds`
  (60), `narrate.drive_idle_seconds` (120).

### 3. Multi-session hunts

- `hunt.py`: remove the single-root refusal in `start()`; the existing
  `hunt.max_active_hunts` cap governs concurrency. The `tick()` scheduler gate
  switches from `active_hunt()` to the cap. This is an invariant change and MUST
  be recorded in `MODULE.md` Section 2 and Section 5.
- Session-scoped verbs: chat-invoked `status`/`log`/`stop`/`pause`/`resume`/
  `review` default to the calling session's bound hunt (`hunt_for_session` with
  both ids). `stop all` stops everything. Non-session bare verbs with multiple
  active hunts list hunts and ask for an id instead of guessing.
- `hooks.py::on_session_start`: auto-bind only when exactly one active hunt exists
  and it has no bindings; otherwise require explicit `attach`.

### 4. Desktop (`desktop/plugin.js`)

- Strip and pane resolve the session durable-key-first
  (`host.state.focusedStoredSessionId`), falling back to the runtime id, then to
  global `/status`.
- Strip shows the focused session's hunt status when bound; otherwise the active
  hunt count plus an attach affordance. Pane shows the `narration_blocked` hint
  when set.

### 5. Installer + docs

- `Makefile install`: after copying the plugin, run a small stdlib script that
  imports `hermes_cli.config` from `$HERMES_HOME/hermes-agent` and sets
  `plugins.entries.swarm-forensics.allow_gateway_injection: true` via
  `load_config`/`save_config`. On any failure, print the manual YAML snippet.
- README and HERMES_DESKTOP.md document the flag and the new verbs.

## Key Decisions

- Chat updates are regular-chat style: batched digests with milestones, tool
  calls, and short rationale, plus continuation prompts that keep session-origin
  hunts driving themselves. No streaming (polling and parsing suffices). Each
  injected message MAY start a model turn when idle; throttling bounds the cost.
  (User decision, 2026-10-04.)
- Injection consent is written by `make install` through Hermes's own config API,
  with docs plus a runtime hint as fallback. The capability registry
  (`hermes_cli/plugin_capabilities.py`) mints no declarable capability for gateway
  injection, so a manifest declaration cannot avoid the config key on this build.
- urlquery stays in the default sources. Tests stay in the lane `tests/`
  directory. (User decisions, 2026-10-04.)
- Injected narration uses the durable `session_key`, never the ephemeral runtime
  session id; the injector resolves the live session by that key.

## Verification

- New Python tests in lane `tests/`: `get_session_env`-based binding; multi-root
  start up to the cap; session-scoped `stop`; narrator digest content, throttle,
  and stall guard; denial flag; injection uses the durable `session_key`.
- New JS tests: stored-id-first lookup; multi-hunt unbound strip state;
  `narration_blocked` hint rendering.
- `make test`, `make lint`, `make check` green. The 5 pre-existing root failures
  in `test_pivot`/`test_replay` (missing `data/viz_mock`) are unrelated and are
  reported, not fixed.
- `make install`, diff the installed copy, then live-check against the running
  Windows app: start two hunts from two chat sessions; confirm digests appear in
  each transcript and both hunts run concurrently.
- Update lane `MODULE.md` (Section 2 invariant change, Section 3 interfaces,
  Section 5 decision log with at most 3 entries), README, HERMES_DESKTOP.md.
  Run `git status`; confirm no stray artifacts. No commit unless asked.
