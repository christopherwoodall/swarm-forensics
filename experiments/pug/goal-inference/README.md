# Goal Inference

Infer agent end-state goals from text fragments and trace evidence.

## Setup

- **Labeled set:** AI Village tasks. The `agent_goals` table gives known goals. Chat messages, memories, code sessions, and computer-use turns group under tasks. (Tables landed 2026-10-04; Stage A pending.)
- **Holdout:** OpenAI trace partitions from `../stylometry/` (`gems`, `traces`, `wiki`, `evals`). Prompts are unobserved. Goals are inferred, never known.

## Documents

- [SOTA.md](SOTA.md): algorithm survey. What matches fragments to goals in 2026.
- [DESIGN.md](DESIGN.md): experimental protocol. Train and validate on village tasks, then apply to the holdout.
- [MODULE.md](MODULE.md): module invariants and interfaces.

## Status

Matcher implemented (`match.py`, stdlib only): leave-one-out validation on the
900 eval questions, anchored sanity checks, holdout inference with confidence
tiers. See [REPORT.md](REPORT.md). Prompt inversion (`invert.py`) mines village
prompt-like content and inverts to the holdout; see [PROMPT_INVERSION.md](PROMPT_INVERSION.md).

## Commands

This lane owns its Makefile; the repo root delegates to it (`make goal-match`, `make goal-invert`).

- `make match`: fragment-to-goal matcher (`MODE=loo|anchored|infer|all`, `FRAG=stride2|drop_top5`).
- `make invert`: prompt inversion, village prompts to holdout (`MODE=mine|map|invert|all`).
- `make all`: the full lane, match through invert.
