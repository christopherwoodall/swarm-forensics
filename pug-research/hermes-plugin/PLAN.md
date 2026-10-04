# PLAN: Recursive Sub-Hunts, Hunter OSINT Sources, Interactive Session Hunts & Session Attach

## Objective
Enable hierarchical swarm hunts, community threat hunter intelligence ingestion, and conversational session steering:
1. **Recursive Sub-Hunts (3 Deep Configurable)**: Allow hunts to spawn child hunts (up to `hunt.max_depth`, default 3) to crawl discovered swarms and leads recursively.
2. **Hunter Sites & Datasets Search**: Target community swarm hunter blogs, GitHub security repos, and arXiv threat intelligence for indicators and datasets.
3. **Interactive Session Hunts & Session Attach**:
   - `/swarm-forensics start [goal]` launches an interactive hunt session that operators can guide in chat like a standard Hermes agent.
   - `/swarm-forensics attach <session_id|hunt_id>` attaches any chat session to a running hunt for live steering.
   - Native Hermes tools for sessions: `sf_spawn_subhunt`, `sf_attach_hunt`, `sf_get_context`, `sf_search_index`, etc.
4. **Desktop UI Tree Visualization**: Display hunt trees, depth badges, child sub-hunts, and attach action.

---

## Invariants & Design Principles
- Invariant 1: Root hunts start only by operator act (desktop button, `/swarm-forensics start`, or armed schedule).
- Invariant 2: Sub-hunts are bounded by `hunt.max_depth` (default 3) and `hunt.max_active_hunts` (default 3 concurrent workers).
- Invariant 10: Model proposes; policy and operator decide.
- Invariant 11: Untrusted fetched text from blogs and datasets MUST be fenced and screened for taint.
- Invariant 19: All SQL MUST be parameterized. Schema migration to v4 with backup `.v3.bak`.
- Simplified Technical English (ASD-STE100) and RFC 2119 imperatives for all code and docs.

---

## Detailed Phases

### Phase 1: Storage Layer (Schema v4 & Migrations)
- In `db.py`: advance schema version to 4.
- Create `.v3.bak` before migration.
- Add `parent_hunt_id TEXT`, `depth INTEGER NOT NULL DEFAULT 0`, and `session_id TEXT` to `hunts` table.
- Update `ledger.py` methods (`create_hunt`, `hunts`, `hunt`, `active_hunts`, `child_hunts`).
- Add settings in `settings.py`:
  - `hunt.max_depth` (int, default 3, min 0, max 10)
  - `hunt.auto_spawn_subhunts` (bool, default True)
  - `hunt.max_active_hunts` (int, default 3, min 1, max 10)
- Add migration unit tests in `tests/test_store.py`.

### Phase 2: Multi-Worker Hunt Service & Recursive Sub-Hunts
- Refactor `HuntService` in `hunt.py` to support multiple concurrent workers up to `hunt.max_active_hunts`.
- Implement `spawn_subhunt(parent_id, goal=None, max_cycles=None)` with depth check `depth <= cfg["hunt.max_depth"]`.
- Update `Engine` in `research.py` to auto-spawn child hunts when new swarms/campaigns or high-priority leads are found (if `hunt.auto_spawn_subhunts` is enabled).
- Implement child hunt lifecycle, event logging, and status reporting.
- Add unit tests in `tests/test_hunt_tree.py`.

### Phase 3: Hunter OSINT Sources & Dataset Ingestion
- Seed hunter intelligence sources in `registry.py` and `db.py` (e.g. GitHub threat intel, arXiv research papers).
- Add hunter query templates in `prompts.py` (searching for swarm C2, agent botnets, indicator datasets).
- Update `research.py` to extract indicators, datasets, and infrastructure from hunter publications.
- Add tests in `tests/test_hunter_sources.py`.

### Phase 4: Interactive Session Hunts, Attach Verb & Session Tools
- Implement `/swarm-forensics attach <hunt_id|session_id>` in `command.py`.
- Update `/swarm-forensics start [goal]` to bind to a session and output an interactive agent briefing for conversational steering.
- Add new Hermes session tools in `agent_tools.py`:
  - `sf_spawn_subhunt(goal, parent_hunt_id, max_cycles)`
  - `sf_attach_hunt(hunt_id)`
- Register tools in `plugins/swarm-forensics/__init__.py`.
- Add unit tests in `tests/test_agent_tools.py` and `tests/test_command.py`.

### Phase 5: REST API & Desktop UI Tree View
- In `dashboard/plugin_api.py`:
  - Support `parent_hunt_id`, `depth`, and `session_id` in hunt endpoints.
  - Add `POST /hunts/{id}/spawn` endpoint to spawn child hunts.
  - Return tree structure in `/hunts`.
- In `desktop/plugin.js`:
  - Display depth chips (`depth: 0`, `depth: 1`, etc.) and parent/child relationships on `HuntPage`.
  - Add `+ Sub-hunt` button on active and selected hunts.
  - Add `Attach` command helper (`/swarm-forensics attach {id}`) on hunts.
  - Add sub-hunt settings to `SettingsPage`.
- Update `tests/render.test.mjs` with fixtures and render tests for sub-hunt elements and depth badges.

### Phase 6: Documentation, Lint & Verification
- Update `MODULE.md` Sections 1-5 (maintain max 3 entries in Section 5).
- Update `README.md` and `SKILL.md`.
- Verify `make test`, `make lint`, `make check` pass with 0 errors.
