# Module: Swarm Forensics Core

## 1. Intent & Scope
Core engine for processing multi-agent logs, reconstructing chronological agent timelines, and detecting coordination anomalies.

## 2. Active Invariants
- Memory-safe stream processing: never load full raw archives into memory.
- All timeline events must conform to the unified forensic schema.
- Replay cases (`replay.py`) MUST come from streamed archives, be masked and length-limited, and pass `validate_case`.
- Replay output MUST NOT claim success, intent, or attack. It MUST label stderr text, missing output, and time-window context.

## 3. Current Interfaces & Dependencies
- Depends on: `data/` loaders, `ingest/` (raw data acquisition, see [ingest/MODULE.md](ingest/MODULE.md))
- Exports: Forensic schemas, event stream parsers, graph builder
- `replay.py`: `export_session(session_id, dir)`, `build_mock_case()`, `validate_case(case)`, `ReplayError`. CLI: `--mock | --session UUID`. Contract: `schema_version` 1, one JSON file per session, written under `data/raw/replay/`.
- Viewer (not a package): `data/viz_mock/v2/serve.py` (loopback, serves `/case.json` plus a fixed public file list) and `workflow-player.html` (fixed camera, text via `textContent`).
- Commands: run through the root `Makefile` (`make help`). Replay targets: `replay-mock`, `replay-export SESSION=<uuid>`, `replay-serve`.

## 4. Current State & Known Gaps
- State: Scaffolding phase. `ingest/` downloads raw data and writes synthetic samples. `replay.py` exports one session as a replay case.
- Gap: Anomaly heuristics engine not yet implemented.
- Gap: The replay exporter scans `computer_use_turns` and `events` once per session (about 40 s). It has no index.
- Gap: Browser behavior has no automated test. Static checks run in `test_replay.py`. Manual checks used agent-browser.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-01 Droid]: Name status `stderr_recorded`, not "error". The dataset `error` field holds stderr, and `git push` writes its normal progress text there.
- [2026-10-01 Droid]: Export one session per case with a fixed camera in the viewer. Ground every step in a source record id.
- [2026-10-01 Droid]: Put data acquisition in the `ingest/` subpackage. It has its own `MODULE.md`.
