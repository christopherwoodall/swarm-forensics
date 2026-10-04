# Module: Stylometry

## 1. Intent & Scope
Compare agent-text corpora through partitioned lexical statistics.
Partitions stay separate. Comparisons run pairwise across partitions.
The module covers OpenAI-side partitions now and AI Village partitions later.

## 2. Active Invariants
- Partitions MUST never merge into one monolith. Each keeps its own counts.
- Builders MUST stream input line by line. They MUST NOT load full tables.
- Silent-locus sources are read-only. Writes stay under this directory.
- Raw village downloads MUST go to `data/raw/` and MUST stay untracked.
- Every comparison run MUST append its parameters and results to `runs_log.jsonl`.
- `lexdb.sqlite` is a build artifact. It MUST stay untracked and regenerable.
- `$HF_TOKEN` MUST come from the environment. Never log or commit it.

## 3. Interfaces & Dependencies
- Implemented: `build_lexdb.py` (`--db`, `--partitions`, `--tokenizers`).
- Implemented: `compare.py` (`--db`, `--pair`, `--method`, `--matrix`).
- Implemented: `fetch_aivillage.sh` (needs granted dataset access).
- Dependencies: Python standard library only. No new packages.
- Commands: run through the root `Makefile` (`make help`).
  Stylometry targets: `stylo-lexdb`, `stylo-compare`.
- Planned: village partition builders in `build_lexdb.py` `PARTITIONS`
  registry (needs dataset access first).

## 4. Current State & Known Gaps
- State: Four OpenAI-side partitions build cleanly (gems, traces, wiki, evals).
- State: 78 comparison runs logged across six pairs (seven methods plus
  N-sensitivity and a corrected Burrows Delta re-run).
- State: Findings are recorded in `REPORT.md`.
- Gap: AI Village data is unreachable. The dataset is gated and the VM
  token lacks granted access (401 on all data files). `fetch_aivillage.sh`
  documents the exact failure and the remedy.
- Gap: Village-side task grouping is designed but unimplemented.
- Gap: No significance thresholds yet. Similarities are descriptive.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Subagent]: Fix Burrows Delta to z-score against the
  four-partition background and re-run. Rationale: two-profile z-scoring is
  degenerate (Delta = 2.0 for every pair). The six bad runs stay in the log
  marked as superseded.
- [2026-10-04 Subagent]: Store village raw downloads under
  `pug-research/stylometry/data/raw/`, not the repo-root `data/raw/`.
  Rationale: the module owns its raw inputs; the parent task names this path
  explicitly. The root AGENTS.md path applies to the core ingest module.
- [2026-10-04 Subagent]: Exclude `pages.jsonl` and the marker-sweep events
  from the lexdb. Rationale: pages double-count revision bodies; the sweep
  notes are analyst prose, not agent text.
