# CAVEATS.md — packet v3 consolidated limitations

Graders read this first. Every limitation below is quoted or paraphrased
from the staged reports themselves. Nothing here is new; it is collected
so no caveat hides inside a single lane's document.

## Stylometry (stylometry-REPORT.md)

1. **Traces contain analyst metadata, not just agent voice.** "eval" and
   "agent" appear in 100% of sampled trace documents. These are analyst
   attribution notes baked into the records. Do not interpret them as
   agent-produced language.
2. **Tokenizer artifact inflates wiki keyness.** The tokenizer strips "%",
   so URL-encoding surfaces as hex fragments ("3a", "2f", "5b"). These
   dominate the wiki's distinctive-term list and are encoding artifacts,
   not vocabulary.
3. **Six degenerate Burrows Delta runs are logged and MUST be ignored.**
   The first six Delta runs returned 2.0 for all pairs (two-profile
   z-scoring collapses). The method was fixed to z-score against the
   four-partition background and re-run. The degenerate runs remain in
   `runs_log.jsonl` marked superseded.
4. **The traces sample is 1-in-20** (29,498 of ~590k lines), deterministic
   stride. Rare patterns may be missed or over-weighted.
5. **Lexical divergence is the current verdict, not the final one.**
   The v1 partitions share only the long tail of ordinary English; their
   cores are disjoint. REPORT_V2 (pending) re-tests this on
   functionally-matched pairs — the v1 conclusion may not survive.

## Goal inference (goal-inference-REPORT.md, goal-inference-DESIGN.md)

6. **Degraded stack.** No sentence-transformers, no torch, no PyPI on this
   VM. The matcher is TF-IDF cosine plus structured feature tokens with a
   heuristic rerank — NOT the bi-encoder/cross-encoder stack in DESIGN.md.
   Do not cite these numbers as SOTA-stack results.
7. **Validation measures fragment recovery, not transfer.** Leave-one-out
   top-1 of 1.0000 (stride-degraded) and 0.9956 (top-5 terms removed) is
   same-distribution question-to-question recovery. It does NOT measure
   true agent-query-to-goal transfer.
8. **No ground truth on the holdout.** Tiers are evidence grades, not
   findings. Inferred holdout goals are hypotheses, never accuracy claims.
9. **Taxonomy gap.** The 900-question taxonomy does not cover the holdout's
   real goals. All 618 gems land Tier 3 (correct negative — the taxonomy
   is eval-shaped, the gems are provider-shaped). Two anchored goals patch
   two holes; the rest of the gap is unmeasured.
10. **Holdout sample bias.** All 400 trace fragments resolve to dsqa_250
    because the sample is dominated by the DoE `zz=oai` cluster. Do not
    generalize beyond that sampling frame.
11. **Domain shift (DESIGN.md).** Village goals are game/CTF-style tasks;
    OpenAI holdout goals are eval-question data-retrieval tasks. A matcher
    tuned on village vocabulary will misfire. Village validation measures
    within-domain generalization only.
12. **Goal granularity mismatch.** A village "goal" (win the round) and an
    OpenAI "goal" (answer one eval question) are different units. Inferred
    holdout goals are scoped to the task family, not the instance.
13. **Prompt unobservability.** The agent's actual prompt is never observed.
    Two different prompts can produce identical traces. Inference stops at
    the best-supported hypothesis.
14. **Structured features are load-bearing.** When features were rerank-only,
    word noise beat them (dsqa_250 ranked 41st on words alone for its own
    traces). Promoting features to first-class stage-1 dimensions fixed it.
    Any reimplementation that demotes structured features will silently
    regress to word-noise results.

## SEED Fire History (seed-firehistory-sweep.md)

15. **Negative result, bounded method.** All June-2026 archive/relay/urlquery
    shapes queried for the NSW Fire History service were clean. This bounds
    the detection method: direct ArcGIS `/query?where=...` interactions may
    leave no archive or relay trace at all. Recovering the original query
    likely requires operator or provider logs. Absence here is expected
    rather than informative for services with no static links.

## 5W operational framework (5w-operational-framework.md)

16. **Framework, not findings.** The 5W document is a detection/SOC
    operationalization proposal. Its "URL basins of attraction" concept is
    a hypothesis about model behavior, not a measured result.

## jqp / SEC lead (jqp-ihme-lead.md)

17. **Direct evidence of a request, not of an operation.** The June 18,
    17:13 UTC jqp/SEC observation is direct evidence of a Massachusetts
    county-extraction request inside the burst window. It links the
    relay/object/task shapes. It does NOT, by itself, prove every archive
    save belonged to one operation or actor.

## Scope (all lanes)

18. **Agents, agent systems, and infrastructure only.** No human/operator
    attribution is attempted or implied anywhere in this packet.
19. **Association vs identity.** Toolkit-family association is supported by
    the evidence; common-operation identity remains unestablished.
    Provider markers, eval/task-family markers, and agent-instance markers
    are three distinct linkage levels — do not collapse them.
