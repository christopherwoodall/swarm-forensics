# Module: Swarm Forensics Core

## 1. Intent & Scope
Develop tools for processing multi-agent logs and exploring coordination through messages and shared artifacts.
The forensic engine remains unimplemented.
Read [PROJECT_BRIEF.md](../../PROJECT_BRIEF.md) for the proposed direction and discussion sources.

## 2. Active Invariants
- Memory-safe stream processing: never load full raw archives into memory.
- All timeline events must conform to the unified forensic schema.

## 3. Interfaces & Dependencies
- Implemented subpackage: `ingest/` for acquisition and synthetic samples. See [ingest/MODULE.md](ingest/MODULE.md).
- Implemented dependencies: `huggingface_hub`; Ruff is a development dependency.
- Planned interfaces: forensic schema, event stream parsers, and graph builder. These are not exported yet.
- Commands: run through the root `Makefile` (`make help`).
- Watcher setup: `make watcher-client`, `make watcher-init`, and `make watcher-read [WATCHER_AFTER=<cursor>]`.
- Watcher dependency: official FairyStack peer client downloaded to ignored `data/raw/fairystack/`.
- Watcher credential: private user configuration outside the repository; public metadata lives in `colette-research/hermes-log/ENROLLMENT.json`.

## 4. Current State & Known Gaps
- State: Acquisition scaffolding. Offline tests, lint, and synthetic sample generation pass.
- State: Discussion sources and open decisions are recorded in the root project brief.
- State: Read [STATUS.md](../../STATUS.md) for the verified checkpoint.
- Gap: The unified forensic schema is not defined.
- Gap: Timeline reconstruction and the graph pipeline are not implemented.
- Gap: Anomaly heuristics engine not yet implemented.
- Gap: Visualization mocks use synthetic data. Real-data integration is not verified.
- Gap: Hermes plugins and FairyStack integration remain proposals or externally reported experiments.
- State: The local silent-watcher identity was initialized. Private file and directory permissions were verified.
- State: Conversation enrollment and authenticated reads are verified. The retained source history is archived under `data/raw/fairystack/`.
- Gap: Watcher commands do not provide automatic polling or ledger extraction.
- State: Watcher setup is paused at Colette's request. Resume from `colette-research/hermes-log/CHECKPOINT.json`.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-01 Hermes]: Use a session-specific external identity for observation. Keep credentials outside version control.
- [2026-10-01 Hermes]: Separate discussion proposals from verified acquisition tooling. Correct the documentation's unimplemented export claims.
- [2026-10-01 Droid]: Put data acquisition in the `ingest/` subpackage. It has its own `MODULE.md`.
