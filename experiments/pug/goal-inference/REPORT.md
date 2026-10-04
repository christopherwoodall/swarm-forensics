# Fragment-to-goal matcher: findings (degraded mode)

## Corrections (2026-10-04 adversarial fix pass)

Every claim below was demoted one epistemic level per `pug-research/REVIEW.md`
objections #2–#8, #13–#15, #18, #19. What changed:

- "Validation" retitled to "Pipeline check on labeled proxy" throughout
  (the module invariant and DESIGN.md:15 withhold the word "validation"
  from non-village work).
- "Independently recovered dsqa_250" → "reproduced": the question text and
  the trace URL contain the identical string `civilrightsdata.ed.gov`; the
  matcher matched the string to itself through `f:dom=`.
- The anchored MA-county check is a retrieval sanity check (target authored
  from the fragment's own features — circular by design, tests plumbing
  only). Its 0.76 is never cited as goal-signal evidence.
- 72 wiki Tier-1 hits demoted to Tier 2: their two "independent" evidence
  types came from the same page. Tier 1 now requires distinct documents.
- The 400-trace dsqa_250 row moved to a sample-composition footnote: the
  sample is one DoE cluster matched 400 times, not 400 inferences.
- Gems Tier 3 reworded as abstention (taxonomy gap), not a correct negative.
- Score floors set (T1 ≥ 0.20 / margin ≥ 0.10 / distinct docs; T2 ≥ 0.12 /
  margin ≥ 0.05); re-tier moved 72 hits T1→T2, zero T2 hits below floors.
- Feature vocabularies (AGENCIES/RELAYS/TRADE_TERMS) disclosed as
  hand-compiled from prior hunt findings (frozen v1); the matcher cannot
  discover goals outside them.
- "Distinctive" in drop_top5 defined in runs.md; MIN_FRAG_TOKENS=8 guard
  added to match.py.
- "Village blocked" statements refreshed: all five tables landed 2026-10-04.
- Note: the stylometry lane is auditing the gems partition (oai-1.3.0
  contamination, REVIEW #1). If it is removed, the 618-gems row below is void.

## Stack status

DESIGN.md specifies a bi-encoder retriever + cross-encoder reranker. This VM
has no sentence-transformers, no torch, and no PyPI. What runs here:

- **Stage 1 (retriever):** TF-IDF cosine over word tokens PLUS structured
  feature tokens (`f:dom=`, `f:param=`, `f:path=`, `f:jq=`, `f:filter=`,
  `f:relay=`, `f:agency=`, `f:year=`), each with their own idf. Structured
  features are first-class dimensions, not an afterthought.
- **Stage 2 (rerank):** a transparent heuristic —
  `0.6 * cosine + 0.4 * type-weighted feature coverage`, with type weights
  (`dom` 3.0, `param`/`agency`/`jq`/`filter` 2.0, `path` 1.5, rest 1.0)
  recorded as run parameters. This is NOT a learned cross-encoder.

Do not cite these numbers as SOTA-stack results. They describe the pipeline
shape and the feature design, not the model class.

## Pipeline check on labeled proxy (not validation per DESIGN.md:15)

The 900 DeepSearchQA questions are a labeled proxy (AI Village tables have
landed but Stage A has not run yet). Fragment = degraded question text;
goal set = all 900 questions.

| Fragment construction | top-1 | top-3 |
|---|---|---|
| stride2 (every 2nd content token) | 1.0000 | 1.0000 |
| drop_top5 (5 highest-idf terms removed; "distinctive" = matcher idf over the question set — see runs.md) | 0.9956 | 0.9967 |

Honest reading: this measures same-distribution fragment recovery, NOT
agent-query-to-goal transfer, and per the module invariant it is a pipeline
check, not validation. The 7 misses are all same-family confusions
(election question -> election question, Shakespeare -> Shakespeare) — the
matcher lands in the right task family when it misses the exact question.
dsqa_691's fragment emptied completely after dropping its top-5 terms
(short question); it is now refused by the MIN_FRAG_TOKENS=8 guard instead
of silently scoring 0.0.

## Retrieval sanity checks (plumbing only — targets partly authored from fragments)

| Fragment | Top-1 goal | cosine | margin |
|---|---|---|---|
| DoE trace: `civilrightsdata.ed.gov/api/v1.0/EntityMeasures?surveyYearKey=5&…&zz=oai…` | dsqa_250 | 0.39 | 0.32 |
| MA-county: jqp fetching `sec.gov/files/county.json` via allorigins, jq `select(.code\|startswith("us-ma-"))` | anchored/sec-county-ma | 0.76 | 0.72 |

The DoE check **reproduced** (not independently recovered) the hunt's
confirmed eval link: dsqa_250's problem text literally contains
`civilrightsdata.ed.gov`, and the trace URL contains the identical string —
the matcher matched the string to itself through `f:dom=`. Rank-1 at cosine
0.184 / margin 0.153 on the noisier GetStateEstimation variant is a
nearest-neighbor result at low absolute score, reported here with the score
so it is not mistaken for a confident match.

The MA-county check is circular by design: `anchored/sec-county-ma` was
hand-authored with the fragment's exact signature (sec.gov domain,
`startswith("us-ma-")`, jq ops). It tests that the retrieval plumbing works
end to end. The 0.76 is plumbing throughput, not goal-signal evidence, and
is never cited as such.

## Holdout inference (1,418 fragments, re-tiered 2026-10-04)

| Partition | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| traces (400, feature-rich sample) | 0 | 400 | 0 |
| wiki (400, tradecraft-dense) | 0 | 392 | 8 |
| gems (618) | 0 | 0 | 618 |

- **400 trace fragments -> dsqa_250 (Tier 2).** Sample-composition footnote:
  the sample is dominated by the DoE `zz=oai` cluster; every fragment
  resolves via the shared domain string `f:dom=civilrightsdata.ed.gov`.
  This row describes the sample, not 400 independent inferences.
- **392 wiki fragments -> anchored/sec-county-ma (Tier 2, was Tier 1).**
  Demoted: the two cited evidence types (`f:dom=sec.gov` +
  `f:relay=jqp/allorigins`) were extracted from the same wiki page — one
  observation, two correlated features. Tier 1 requires distinct documents.
- **618 gems -> Tier 3 (abstention).** The 900-question taxonomy cannot cover
  gem names/code by construction; the matcher abstained for lack of
  vocabulary, which is a taxonomy gap, not a correct negative. A correct
  negative would require a plausible-but-wrong goal that was rejected.

## Feature-vocabulary provenance

`AGENCIES`, `RELAYS`, `TRADE_TERMS` in match.py (frozen v1, 2026-10-04) were
compiled by hand from prior hunt findings. Holdout traces touching known
incident agencies receive features; traces from novel agencies receive
none. The matcher cannot discover goals outside this vocabulary; recall on
novel agencies is unmeasured and no claim about it is made.

## Most carefully stated single result

Fragment (trace): `https://civilrightsdata.ed.gov/api/v1.0/GetStateEstimation?survey_Year_Key=6&Measure_Id=5&State_Id=17&zz=oai17816867393133738`
-> dsqa_250 (Tier 2, rerank score 0.184, margin 0.153), evidence:
`f:dom=civilrightsdata.ed.gov` — a string present verbatim in both the
question text and the URL. This reproduces the hunt's confirmed link through
the feature pipeline at low absolute score. It is the strongest
cross-distribution result in this lane and it is weak; that is the honest
headline.

## Bugs found and fixed during the runs

1. `features_from_question` used the regex group instead of the full match:
   every year became `f:year=20`. Fixed with `finditer` + `group(0)`.
2. `www.` subdomains (`www.sec.gov`) mismatched bare domains (`sec.gov`).
   Hosts are now normalized at feature extraction.
3. First rerank was too weak to matter: the cosine shortlist (top-20)
   excluded dsqa_250 for most DoE traces (rank 41 on words alone), so the
   rerank never saw it. Fixed by promoting features to stage-1 dimensions
   instead of rerank-only. DESIGN.md Honest-limits #3 predicted this; the
   run confirms the design doc rather than discovering it.

## Ablations & diagnostics (2026-10-04, stdlib-only; see ablations.json)

1. **Feature-family ablation:** on same-distribution LOO, lexical-only
   reaches 0.92–0.96 top-1 and structured-only 0.15; hybrid adds ~5 points
   (0.97–0.98) — but the ablation only exercises {dom, year, agency} because
   eval questions contain no URLs, relays, or jq, so the cross-distribution
   value of the other families is untested here.
2. **Per-family importance:** leave-one-family-out moves LOO top-1 only for
   `year` (−0.044); dom/param/path/jq/filter/relay/agency each cost ≤0.001,
   and dsqa_250 stays rank-1 without any single family (its signal is
   redundant across families).
3. **Village cross-task confusion:** leave-one-agent-out goal prediction
   from chat fragments scores 0.03 ≈ chance (1/25 goals) — village chat
   vocabulary does not identify village goals; the goal signal lives in
   actions, not chat.
4. **Prompt-element ablation:** tool-inventory prompt elements predict
   observed behavior best (largest deltas: +130 chars/msg, +0.13 list rate,
   +0.07 URL rate); guardrail deltas are uninterpretable (42 vs 4 agents).
5. **Evidence-type breakdown:** holdout prompt inferences rest on structural
   evidence (47%) and URL evidence (36%), prose/other 17% — the inversion
   is blind to anything not encoded in URL or structural form.

## Honest limits (unchanged)

- No ground truth on the holdout. Tiers are evidence grades, not findings.
- The 900-question taxonomy does not cover the holdout's real goals
  (no crowdfunding question; gems uncovered). Anchored goals patch two
  holes; the rest of the taxonomy gap is unmeasured.
- Only one real agent-query-to-goal pair exists (dsqa_250). The pipeline
  check numbers do not transfer to that setting.
- No LLM judge, no clustering pass. Stage B's open-set discovery step is
  not implemented in degraded mode.
- Village tables landed 2026-10-04; Stage A (leave-one-task-out on real
  village tasks) is unblocked but not yet run.
