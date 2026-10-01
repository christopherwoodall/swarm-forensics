# Module: Swarm Forensics Core

## 1. Intent & Scope
Core engine for processing multi-agent logs, reconstructing chronological agent timelines, and detecting coordination anomalies.

## 2. Active Invariants
- Memory-safe stream processing: never load full raw archives into memory.
- All timeline events must conform to the unified forensic schema.

## 3. Current Interfaces & Dependencies
- Depends on: `data/` loaders
- Exports: Forensic schemas, event stream parsers, graph builder

## 4. Current State & Known Gaps
- State: Scaffolding phase.
- Gap: Anomaly heuristics engine not yet implemented.

## 5. Pruned Decisions (Keep max 3)
- [Initial Setup]: Seeded initial blackboard structure.
