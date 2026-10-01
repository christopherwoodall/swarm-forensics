# Module: Swarm Forensics Core

## 1. Intent & Scope
Core engine for processing multi-agent logs, reconstructing chronological agent timelines, and detecting coordination anomalies.

## 2. Active Invariants
- Memory-safe stream processing: never load full raw archives into memory.
- All timeline events must conform to the unified forensic schema.

## 3. Current Interfaces & Dependencies
- Depends on: `data/` loaders, `ingest/` (raw data acquisition, see [ingest/MODULE.md](ingest/MODULE.md))
- Exports: Forensic schemas, event stream parsers, graph builder
- Commands: run through the root `Makefile` (`make help`).

## 4. Current State & Known Gaps
- State: Scaffolding phase. `ingest/` downloads raw data and writes synthetic samples.
- Gap: Anomaly heuristics engine not yet implemented.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-01 FairyStack]: Record Jessald's authorization for merges without human review. Retain test, lint, and conflict gates.
- [2026-10-01 FairyStack]: Use a documentation-only test branch to verify GitHub collaboration from the Multi app box.
- [2026-10-01 Droid]: Put data acquisition in the `ingest/` subpackage. It has its own `MODULE.md`.
