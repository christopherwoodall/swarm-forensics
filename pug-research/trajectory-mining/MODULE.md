# Module: Trajectory Mining

## 1. Intent & Scope
Index the AI Village archives in `data/raw/`. Let a user pick traces from different agents. Show them in a 3D graph. Each agent sits at the top. The stated goal sits at the bottom. The graph links agents through artifacts and shared language. The module shows recorded evidence. It does not claim that an agent achieved a goal.

Scope: computer-use sessions and turns, Claude Code sessions and messages, chat messages and events, village goals and agent goals. Out of scope: screenshots, `agent_memories` text, and typed text.

## 2. Active Invariants
- The importer MUST stream each archive once. It MUST NOT load a whole table into memory.
- The index MUST carry `meta.schema_version`. A version mismatch MUST stop the run with a rebuild message. `--rebuild` MUST be the only way to delete an index.
- Every edge MUST carry one evidence class: `recorded`, `rule_derived`, or `inferred`. Edge claims MUST NOT use words such as `achieved`, `completed`, or `solved`.
- Goal links MUST be `rule_derived` from a time window. A goal ends at the next goal start in the same group. Chat episodes split on a 30-minute silence gap.
- Shared-language links MUST be `rule_derived`. The module MUST report a link only when at least two agents share the feature. It MUST cap each feature at 10 owners.
- LLM links MUST be `inferred`. The LLM MUST stay off unless the user passes `--enable-llm`, a model, and `max_usd`. It MUST read credentials from the environment. It MUST stop when the budget is reached. It MUST drop any link without a valid citation.
- The importer MUST mask credentials with `contract.sanitize_text`. It MUST NOT store typed text. Errors and logs MUST NOT include record values.
- The viewer MUST bind to loopback, read the index read-only, serve a fixed file list, and write DOM text with `textContent`.
- Graph queries MUST be bounded. The catalog MUST aggregate actions into buckets and report hidden nodes and gaps in `meta`.
- Tests MUST use synthetic data and MUST NOT use the network.

## 3. Interfaces & Dependencies
- Depends on: Python 3.12 standard library, `pyyaml` (LLM config), `ruff` (dev), vendored `three.js` under `vendor/`. Data comes from `data/raw/`.
- Commands (run in this directory through `make`):
  - `make index [DATA_DIR] [DB_PATH]`: stream all tables into the v2 index. Resumable by table checkpoints. Default `DB_PATH`: `../../data/raw/trajectories/index-v2.db`. When the target sits on `/mnt/`, the importer builds in `~/.cache/trajectory-mining/` and moves the finished file into place. An interrupted run resumes from that staging file.
  - `make index-sample LIMIT=<n> DB_PATH=<file>`: read at most `n` rows per table.
  - `make index-memories`: also count `agent_memories` rows.
  - `make report`: print the coverage report (rows read, skipped, unsupported shapes, join rates, disk, timing).
  - `make serve | start | stop | status | restart [PORT=8002]`: run the viewer.
  - `make llm TRACES="session:<id> ..." MODEL=<name> MAX_USD=<n>`: opt-in link hypotheses. Config template: `llm.example.yaml`.
  - `make test`, `make lint`, `make clean`.
- Python modules:
  - `contract.py`: `SCHEMA_VERSION` (2), `sanitize_text`, graph types, `validate_trajectory_payload`, `ContractError`.
  - `db.py`: `connect(path, create, readonly)`, `INDEX_SCHEMA_VERSION` (2), `IndexVersionError`.
  - `extract.py`: `extract_turn`, `extract_cc_message`, `extract_artifacts`, `classify_action`.
  - `importer.py`: `TrajectoryImporter`, `main`. Flags: `--limit`, `--rebuild`, `--force`, `--memories`, `--report`.
  - `episodes.py`: `build_episodes`. `goals.py`: `resolve_windows`, `build_goal_links`. `language.py`: `build_language_links`. `report.py`: `coverage_report`.
  - `catalog.py`: `TraceCatalog.overview | search_traces | graph | steps`.
  - `llm.py`: `run_analysis`, `resolve_settings`, `parse_response`.
  - `serve.py`: `make_server(port, db_path, quiet)`.
- HTTP API (read-only, loopback): `/api/overview`, `/api/traces`, `/api/graph`, `/api/steps`. Graph payload follows `contract.SCHEMA_VERSION`.
- Index tables: `meta`, `checkpoints`, `shape_counts`, `agents`, `rooms`, `goals`, `sessions`, `turns`, `messages`, `events`, `artifacts`, `episodes`, `episode_members`, `goal_links`, `language_links`, `llm_runs`, `llm_links`.
- Output: one SQLite file under `data/raw/trajectories/` (untracked).

## 4. Current State & Known Gaps
- State: `make test` (80 offline tests) and `make lint` pass.
- State: Sample run, 100,000 rows per table, `LIMIT=100000`: 548 MB index, 78,362 sessions, 671 chat episodes, 112,224 goal links, 25,927 shared language features. It took about 1 minute with the index on a Linux path. It took about 9.5 minutes when SQLite wrote directly on `/mnt/c` (about 10x slower), which is why the importer now stages on a Linux path.
- State: The viewer loads that sample in a browser. Checked: trace search, multi-trace load, shared goal node, hidden-node note.
- Gap: No full-archive run yet. Full-run time and disk are not measured. The importer estimates disk before it starts.
- Gap: Sample joins are incomplete, because each table is cut at its first rows. Many sessions have no turns in the sample.
- Gap: `agent_memories` text is not indexed. Some `computer_use_turns` and `claude_code_messages` shapes are counted as unsupported. The coverage report lists them.
- Gap: Chat episodes show who spoke. They do not show who answered whom.
- Gap: Goal-label overlap remains in the viewer when many goal nodes share one row.
- Gap: The LLM path is tested with mocks only. No real model call has run.
- Gap: The older `index.db` and its WAL file in `data/raw/trajectories/` are not used. The v2 index does not read them.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-02 Droid]: Rewrite the importer against real record shapes and add a versioned v2 index. The earlier prototype guessed field names and cannot be repaired by a patch.
- [2026-10-02 Droid]: Make shared-language and time-window goal links `rule_derived`. Keep `inferred` for LLM output only, so each edge shows how it was made.
- [2026-10-02 Droid]: Keep the work local in `pug-research/trajectory-mining/` with its own `Makefile`. Root `Makefile` and `src/` stay unchanged.
