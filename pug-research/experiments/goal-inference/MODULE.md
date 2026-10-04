# Module: Goal Inference

## 1. Intent & Scope
Infer agent end-state goals from lexical fragments and trace evidence.
Train and validate the fragment-to-goal matcher on labeled AI Village tasks.
Apply the validated matcher to the unlabeled OpenAI trace partitions as a holdout.
Holdout inferences are hypotheses. They MUST cite supporting trace evidence.
Read [DESIGN.md](DESIGN.md) for the protocol and [SOTA.md](SOTA.md) for the method survey.

## 2. Active Invariants
- Stream raw tables. Never load a full table into memory.
- Raw downloads stay untracked under `data/raw/`.
- Holdout goal labels MUST carry a confidence tier and trace-evidence citations.
- No holdout inference may claim a known prompt or confirmed task. The prompt is unobserved.
- Reported metrics MUST come from the labeled AI Village split only, with
  one permitted exception: labeled-proxy pipeline checks (e.g. leave-one-out
  over DeepSearchQA questions) may be reported ONLY when explicitly titled
  as non-validation pipeline checks per DESIGN.md:15. Holdout has no ground
  truth; holdout outputs are hypotheses, never accuracy claims.

## 3. Interfaces & Dependencies
- Consumes partitions from `../stylometry/` (gems, traces, wiki, evals) when ready.
- Consumes AI Village by-task partitions (chat, memories, goals, code, computer-use); tables landed 2026-10-04.
- Planned commands (not implemented): `goal-train`, `goal-eval`, `goal-infer`. Each gets a root Makefile target with a `##` description before use.
- Implemented: `make goal-match` (match.py: LOO pipeline check, anchored
  retrieval sanity checks, holdout inference with tiering), `make goal-invert`
  (invert.py: prompt mining, prompt->behavior map, evidence-grounded holdout
  prompt hypotheses). Both degraded-mode (TF-IDF + heuristic rerank / rules),
  stdlib-only per VM constraints.
- Planned dependency: a sentence-embedding model and a cross-encoder reranker. See [SOTA.md](SOTA.md) for the selection rationale.

## 4. Current State & Known Gaps
- State: Fragment-to-goal matcher implemented in degraded mode (TF-IDF +
  heuristic rerank; see REPORT.md). Prompt-inversion pipeline implemented
  (invert.py: mine/map/invert).
- State: AI Village tables landed 2026-10-04 (chat, memories, goals, code,
  computer-use). Labeled-split validation (Stage A) is unblocked but not
  yet run; current metrics are labeled-proxy pipeline checks only.
- Gap: No goal taxonomy for the OpenAI holdout exists. Discovery is open-set
  and not yet implemented (no clustering pass, no LLM judge).
- Gap: Non-linguistic fragments (URLs, query params, jq filters) carry goal
  signal that text embeddings may miss. Structured trace features are
  first-class stage-1 dimensions in the degraded matcher (see REPORT.md
  bug #3); the SOTA stack is still pending a machine with PyPI access.
- Gap: Feature vocabularies (AGENCIES/RELAYS/TRADE_TERMS) are frozen v1,
  hand-compiled from prior hunt findings. The matcher cannot discover goals
  outside them; recall on novel agencies is unmeasured.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Agent]: Adversarial fix pass (REVIEW #2-#8, #13-#15, #18, #19): demoted every claim one epistemic level; "validation"->"pipeline check"; dsqa_250 "reproduced" not "independently recovered"; anchored MA-county is plumbing-only; 72 wiki T1->T2; score floors set and re-tiered; feature-vocabulary provenance disclosed and frozen v1.
- [2026-10-04 Agent]: Run degraded mode (TF-IDF + heuristic rerank, stdlib+numpy only). Structured features are first-class stage-1 dimensions; word-noise wins when they are rerank-only.
- [2026-10-04 Agent]: Treat the holdout as open-set goal discovery, not closed-set classification. The OpenAI goal taxonomy is unknown.
