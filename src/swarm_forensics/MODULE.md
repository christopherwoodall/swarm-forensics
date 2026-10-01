# Module: Swarm Forensics Core

## 1. Intent & Scope
Develop tools for processing multi-agent logs and exploring coordination through messages and shared artifacts.
The forensic engine remains unimplemented.
Read [PROJECT_BRIEF.md](../../PROJECT_BRIEF.md) for the proposed direction and discussion sources.

## 2. Active Invariants
- Memory-safe stream processing: never load full raw archives into memory.
- All timeline events must conform to the unified forensic schema.
- Replay cases (`replay.py`) MUST come from streamed archives, be masked and length-limited, and pass `validate_case`.
- Replay output MUST NOT claim success, intent, or attack. It MUST label stderr text, missing output, and time-window context.

## 3. Interfaces & Dependencies
- Implemented subpackage: `ingest/` for acquisition and synthetic samples. See [ingest/MODULE.md](ingest/MODULE.md).
- Implemented dependencies: `huggingface_hub`; Ruff is a development dependency.
- Planned interfaces: forensic schema, event stream parsers, and graph builder. These are not exported yet.
- `replay.py`: `export_session(session_id, dir)`, `build_mock_case()`, `validate_case(case)`, `ReplayError`. CLI: `--mock | --session UUID`. Contract: `schema_version` 1, one JSON file per session, written under `data/raw/replay/`.
- `pivot.py`: `validate_graph(graph)`, `load_graph(path)`. CLI: `--file`. It checks the shape of the aggregate pivot graph (layers source, launcher, pivot, target). Source nodes need a confidence badge. Source edges need a confidence. It does not rebuild the counts.
- Viewer (not a package): `data/viz_mock/v2/serve.py` (loopback, serves `/case.json` plus a fixed public file list) and `workflow-player.html` (fixed camera, text via `textContent`). `data/viz_mock/v3_transluce/` follows the same pattern for the pivot graph, with its own `serve.py`.
- Commands: run through the root `Makefile` (`make help`). Replay targets: `replay-mock`, `replay-export SESSION=<uuid>`, `replay-serve`. Pivot targets: `pivot-check`, `pivot-serve`.

## 4. Current State & Known Gaps
- State: Acquisition scaffolding. `ingest/` downloads raw data and writes synthetic samples. `replay.py` exports one session as a replay case.
- State: Offline tests, lint, and synthetic sample generation pass.
- State: Discussion sources and open decisions are recorded in the root project brief.
- State: Read [STATUS.md](../../STATUS.md) for the verified checkpoint.
- Gap: The unified forensic schema is not defined.
- Gap: Timeline reconstruction and the graph pipeline are not implemented.
- Gap: Anomaly heuristics engine not yet implemented.
- Gap: The replay exporter scans `computer_use_turns` and `events` once per session (about 40 s). It has no index.
- Gap: The pivot graph counts come from another investigation and have no event ids. Nothing here re-derives them. Source-layer links are confirmed, candidate, or hypothesized by the other investigation. This repo does not test them.
- Gap: Other visualization mocks use synthetic data. Real-data integration is not verified.
- Gap: Browser behavior has no automated test. Static checks run in `test_replay.py`. Manual checks used agent-browser.
- Gap: Hermes plugins and FairyStack integration remain proposals or externally reported experiments.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-01 Droid]: Check the pivot graph file by shape only. The counts have no source rows in this repo, so the viewer labels them as unverified.
- [2026-10-01 Droid]: Name status `stderr_recorded`, not "error". The dataset `error` field holds stderr, and `git push` writes its normal progress text there.
- [2026-10-01 Hermes]: Separate discussion proposals from verified acquisition tooling. Correct the documentation's unimplemented export claims.
