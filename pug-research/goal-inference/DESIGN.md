# Design: fragment-to-goal matcher

## Objective

Build a matcher that maps text fragments to agent end-state goals.
Measure it where goals are known (AI Village). Apply it where they are not (OpenAI holdout).

## Data

| Split | Source | Labels | Partitions |
|---|---|---|---|
| Labeled | AI Village (`agent_goals` + chat, memories, code, computer-use grouped by task) | Known per task | `village_chat`, `village_memories`, `village_goals`, `village_code`, `village_computer` |
| Holdout | OpenAI trace corpus via `../stylometry/` | None | `gems`, `traces`, `wiki`, `evals` |

Note: AI Village tables landed 2026-10-04; the design runs in full once
Stage A executes on the labeled split. Interim work may use synthetic
village-shape data for pipeline testing only. No interim result counts as
validation.

## Stage A: labeled validation (AI Village)

### Fragment construction

Each training example is a fragment: a short window of agent-produced text (one chat message, one memory entry, one code-turn summary, one trace record's text fields). Fragments group under their task's goal. Keep fragments short (under 200 tokens). Record the fragment type.

### Protocol: leave-one-task-out cross-validation

1. Hold out all fragments from one task. Train on the rest.
2. Predict the held-out fragments' goal from the remaining goal taxonomy.
3. Repeat per task. Report macro-averaged metrics.

This protocol tests generalization to unseen tasks, which is the skill the holdout needs.

### Models to compare

- Baseline 1: TF-IDF + logistic regression.
- Baseline 2: BERTopic clusters mapped to goals by majority vote.
- Baseline 3: bi-encoder zero-shot (fragment vs goal-description cosine).
- Candidate: bi-encoder retriever (top-20 goals) + cross-encoder reranker. See SOTA.md.
- Candidate with tuning: the candidate fine-tuned on village fragments (IFT-style), encoder only.

### Metrics

Top-1 and top-3 accuracy, macro F1 over goals, and calibration (predicted confidence vs empirical accuracy per bin). Report per fragment type. Short non-linguistic fragments get their own error analysis.

### Ablations

- With and without goal descriptions (goal IDs only vs ID + description text).
- With and without structured trace features (target domain, parameter names) appended to the fragment.
- Per-partition training (chat only, memories only) vs pooled.

### Runs log

Every run records: model, hyperparameters, fragment construction rule, split seed, metrics. Append to `runs.md`. Multiple runs with different parameters are expected.

## Stage B: holdout inference (OpenAI partitions)

The holdout has no ground truth. Outputs are hypotheses, never accuracy claims.

### Pipeline

1. **Cluster.** Embed holdout fragments per partition. Cluster (HDBSCAN via BERTopic-style pipeline).
2. **Propose.** For each cluster, LLM-as-judge drafts a goal description from the cluster's most representative fragments.
3. **Ground.** Each proposed goal MUST cite concrete trace evidence: target URLs, query parameters, tool calls, relay paths, or filters (e.g. the Massachusetts-county jq filter). A goal with no evidence citation is rejected.
4. **Score.** Cross-encoder reranker scores fragment-to-proposed-goal fit as a second opinion. Disagreement between the LLM judge and the reranker lowers the confidence tier.
5. **Tier.** Assign confidence:
   - Tier 1: multiple independent trace evidence types support the goal.
   - Tier 2: single evidence type, or judge/reranker disagreement.
   - Tier 3: cluster-coherent but evidence-thin. Report as speculative.

### Anchored examples (sanity checks, not training data)

- The Massachusetts-county jq filter on `sec.gov/files/county.json` implies a subnational-extraction goal.
- The DoE counselor-ratio query implies the `dsqa_250` question goal.
- The matcher should recover goals of this shape. If it cannot, the pipeline is broken.

## Honest limits

1. **No ground truth on the holdout.** Inferred goals are hypotheses graded by evidence, not findings.
2. **Domain shift.** Village goals are game/CTF-style tasks. OpenAI holdout goals are eval-question tasks (data retrieval from live sites). A matcher tuned on village vocabulary will misfire. The leave-one-task-out protocol measures within-domain generalization only.
3. **Non-linguistic signal.** Much of the holdout is URLs, query strings, and parameter names. Text embeddings underweight this. Structured trace features (target, endpoint, params, relay path) carry the goal signal and need first-class treatment.
4. **Goal granularity mismatch.** A village "goal" (win the round) and an OpenAI "goal" (answer one eval question) are different units. Inferred holdout goals should be scoped to the task family, not the instance.
5. **Prompt unobservability.** The agent's actual prompt is never observed. Two different prompts can produce identical traces. Inference stops at the best-supported hypothesis.
6. **Village data landed; Stage A not yet run.** All five AI Village tables
   landed 2026-10-04. The labeled-split validation is unblocked but pending
   execution; until it runs, the only metrics in this lane are labeled-proxy
   pipeline checks.

## Definition of done for this lane

- Stage A metrics on real village data, with runs log and ablations.
- Stage B hypotheses for each OpenAI partition, each with evidence citations and confidence tiers.
- A written statement of which holdout hypotheses survived the evidence bar and which did not.
