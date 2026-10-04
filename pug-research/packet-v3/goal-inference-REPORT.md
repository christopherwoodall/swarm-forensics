# Fragment-to-goal matcher: findings (degraded mode)

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

Do not cite these numbers as SOTA-stack results. They validate the pipeline
shape and the feature design, not the model class.

## Validation: leave-one-out over 900 eval questions

The 900 DeepSearchQA questions are the labeled proxy (AI Village is gated).
Fragment = degraded question text; goal set = all 900 questions.

| Fragment construction | top-1 | top-3 |
|---|---|---|
| stride2 (every 2nd content token) | 1.0000 | 1.0000 |
| drop_top5 (5 most distinctive terms removed) | 0.9956 | 0.9967 |

Honest reading: this measures same-distribution fragment recovery, NOT
agent-query-to-goal transfer. The 7 misses are all same-family confusions
(election question -> election question, Shakespeare -> Shakespeare) — the
matcher lands in the right task family when it misses the exact question,
which is the correct failure mode for goal inference. One degenerate case:
dsqa_691's fragment emptied completely after dropping its top-5 terms
(short question), scoring 0.0. Short fragments need a minimum-token guard.

## Anchored sanity checks (real trace fragments)

| Fragment | Top-1 goal | cosine | rerank |
|---|---|---|---|
| DoE trace: `civilrightsdata.ed.gov/api/v1.0/EntityMeasures?surveyYearKey=5&…&zz=oai…` | dsqa_250 | 0.39 | 0.32 |
| MA-county: jqp fetching `sec.gov/files/county.json` via allorigins, jq `select(.code\|startswith("us-ma-"))` | anchored/sec-county-ma | 0.76 | 0.72 |

Both pass. The DoE check recovers the hunt's one confirmed eval link from
the trace alone. The MA-county check proves structured features (jq ops,
filter values, relay chain) carry goal signal that prose never could —
the 900 questions contain no crowdfunding question, so only the anchored
goal with its feature signature can fire.

## Holdout inference (1,418 fragments)

| Partition | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| traces (400, feature-rich sample) | 0 | 400 | 0 |
| wiki (400, tradecraft-dense) | 72 | 320 | 8 |
| gems (618) | 0 | 0 | 618 |

- **All 400 trace fragments -> dsqa_250 (Tier 2).** The sample is dominated
  by the DoE `zz=oai` cluster; every fragment resolves to the confirmed
  question via `f:dom=civilrightsdata.ed.gov`. Single evidence type, hence
  Tier 2 — the tiering is conservative by design.
- **72 Tier-1 wiki fragments -> anchored/sec-county-ma**, each citing two
  independent evidence types (`f:dom=sec.gov` + `f:relay=jqp/allorigins`).
  These are the swarm's own coordination pages (`dse~StartSeite`,
  `dse~AgentMySecLinksZZZ2`, …) enumerating county.json URL variants.
- **618 gems -> Tier 3 across the board.** No goal in the 900-question
  taxonomy covers gem names/code. Correct negative: the taxonomy is
  eval-shaped and the gems are provider-shaped.

## Most convincing single inference

Fragment (trace `cf22725e…`):
`https://civilrightsdata.ed.gov/api/v1.0/GetStateEstimation?survey_Year_Key=6&Measure_Id=5&State_Id=17&zz=oai17816867393133738`
-> **dsqa_250** (Tier 2, score 0.184, margin 0.153), evidence:
`f:dom=civilrightsdata.ed.gov`. The goal text asks for counselor-to-
bullying-victim ratios from civilrightsdata.ed.gov for 2017-2018 — the
matcher independently recovered the hunt's confirmed link from a bare
API trace, with no prose overlap to lean on.

## Bugs found and fixed during the runs

1. `features_from_question` used the regex group instead of the full match:
   every year became `f:year=20`. Fixed with `finditer` + `group(0)`.
2. `www.` subdomains (`www.sec.gov`) mismatched bare domains (`sec.gov`).
   Hosts are now normalized at feature extraction.
3. First rerank was too weak to matter: the cosine shortlist (top-20)
   excluded dsqa_250 for most DoE traces (rank 41 on words alone), so the
   rerank never saw it. Fixed by promoting features to stage-1 dimensions
   instead of rerank-only. Lesson: if structured features are second-class
   anywhere in the pipeline, word noise wins.

## Honest limits (unchanged from DESIGN.md)

- No ground truth on the holdout. Tiers are evidence grades, not findings.
- The 900-question taxonomy does not cover the holdout's real goals
  (no crowdfunding question; gems uncovered). Anchored goals patch two
  holes; the rest of the taxonomy gap is unmeasured.
- Only one real agent-query-to-goal pair exists (dsqa_250). The LOO
  numbers do not transfer to that setting.
- No LLM judge, no clustering pass, no village data. Stage B's open-set
  discovery step is not implemented in degraded mode.
