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
- `pivot.py`: `validate_graph(graph)`, `load_graph(path)`. CLI: `--file`. It checks the shape of the aggregate pivot graph (layers source, launcher, pivot, target). Source nodes need a confidence badge. Source edges need a confidence. It does not rebuild the counts.
- Viewer (not a package): `data/viz_mock/v2/serve.py` (loopback, serves `/case.json` plus a fixed public file list) and `workflow-player.html` (fixed camera, text via `textContent`). `data/viz_mock/v3_transluce/` follows the same pattern for the pivot graph, with its own `serve.py`.
- Commands: run through the root `Makefile` (`make help`). Replay targets: `replay-mock`, `replay-export SESSION=<uuid>`, `replay-serve`. Pivot targets: `pivot-check`, `pivot-serve`.

## 4. Current State & Known Gaps
- State: Scaffolding phase. `ingest/` downloads raw data and writes synthetic samples. `replay.py` exports one session as a replay case.
- Gap: Anomaly heuristics engine not yet implemented.
- Gap: The replay exporter scans `computer_use_turns` and `events` once per session (about 40 s). It has no index.
- Gap: The pivot graph counts come from another investigation and have no event ids. Nothing here re-derives them. Source-layer links are confirmed, candidate, or hypothesized by the other investigation. This repo does not test them.
- Gap: Browser behavior has no automated test. Static checks run in `test_replay.py`. Manual checks used agent-browser.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-01 Droid]: Check the pivot graph file by shape only. The counts have no source rows in this repo, so the viewer labels them as unverified.
- [2026-10-01 Droid]: Name status `stderr_recorded`, not "error". The dataset `error` field holds stderr, and `git push` writes its normal progress text there.
- [2026-10-01 Droid]: Export one session per case with a fixed camera in the viewer. Ground every step in a source record id.
