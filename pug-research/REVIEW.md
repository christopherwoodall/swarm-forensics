# Adversarial review: pug-research hackathon lanes

**Verdict: the goal-inference lane's headline results are circular by construction, and the stylometry lane's provider-marker finding counts a third-party library as an OpenAI marker — fix the oai-1.3.0 contamination and demote every "validation" claim one epistemic level before a grader does it for you.**

Ranked by damage. Each item names the exact claim and the concrete fix.

---

## 1. Finding 3's "oai" evidence is the OAI-PMH library, not an OpenAI marker
**Target:** `pug-research/stylometry/REPORT.md:58` — "The 'oai' marker appears in gem names, trace attribution, and wiki text."
**Why it hurts:** Of the 814 "oai" tokens counted in the gems partition, 797 come from a single directory: `oai-1.3.0`, the legitimate upstream Ruby gem for OAI-PMH (Open Archives Initiative) harvesting (`lib/oai/client.rb`, `oai.rb`, etc.). It has nothing to do with OpenAI. Worse, `WORD_RE` (`build_lexdb.py:35`, `[a-z0-9]+`) tokenizes whole words, so agent-chosen names like `agentoaitestabc123-0.0.1` do NOT contribute to the "oai" count at all — the report's "appears in gem names" is false at the token level. The count is gem *code*, and the code is third-party. A grader greps the gem dir in ten seconds and the finding collapses.
**Fix:** Exclude `oai-1.3.0` (or all non-agent-authored code) from the gems partition, recount, and restate Finding 3 as names-only. If the dir stays for provenance, count marker tokens in dirnames separately from file bodies and report both.

## 2. The headline validation numbers violate the lane's own invariant
**Target:** `pug-research/goal-inference/MODULE.md:15` ("Reported metrics MUST come from the labeled AI Village split only") vs `pug-research/goal-inference/REPORT.md` "## Validation: leave-one-out over 900 eval questions" (top-1 = 1.0000).
**Why it hurts:** The module invariant forbids exactly what the report's headline section does: reporting metrics from a non-village labeled proxy. A hostile grader doesn't need statistics to kill this — it's a self-contradiction in your own docs.
**Fix:** Either amend the invariant to permit disclosed labeled-proxy validation, or demote the LOO numbers to a "pipeline smoke test" section and strip the word "Validation" from the header. Do one, in both files, today.

## 3. The dsqa_250 "independent recovery" is string equality through a feature pipeline
**Target:** `pug-research/goal-inference/REPORT.md:78-79` — "the matcher independently recovered the hunt's confirmed link from a bare API trace, with no prose overlap to lean on."
**Why it hurts:** dsqa_250's problem text literally contains the string `civilrightsdata.ed.gov`. `features_from_question` (`match.py:122-135`) extracts `f:dom=civilrightsdata.ed.gov` from the question; `features_from_url` (`match.py:93-119`) extracts the identical token from the trace. The matcher matched the string to itself. "No prose overlap" is false — the overlap is verbatim, just routed through `f:dom=`. And "independently" is doing fraudulent work: the features were designed by the same team after the link was known. The honest verb is "reproduced." Also note the absolute score: cosine 0.184, margin 0.153 — rank-1 out of 900 at 0.184 is a nearest-neighbor lottery ticket, not a confident match.
**Fix:** Replace "independently recovered" with "reproduced"; disclose that both sides contain the identical domain string; report absolute scores and margins next to every rank claim.

## 4. The anchored MA-county check builds the lock and the key together
**Target:** `pug-research/goal-inference/REPORT.md` anchored table (cosine 0.76) — "proves structured features carry goal signal that prose never could."
**Why it hurts:** `anchored/sec-county-ma` is a goal the experimenters hand-authored with the fragment's exact signature (`sec.gov` domain, `startswith("us-ma-")` filter, jq ops). Of course TF-IDF retrieves it at 0.76 — you wrote the target to contain the query's tokens. This is a retrieval sanity check, not proof of "goal signal." Presented as the lane's canonical positive, it teaches a grader to distrust every other number in the report.
**Fix:** Relabel as "retrieval sanity check (target authored from fragment features — circular by design, tests plumbing only)." Never cite the 0.76 as evidence that features carry goal signal.

## 5. Tier-1 "two independent evidence types" come from one wiki page
**Target:** `pug-research/goal-inference/REPORT.md` — "72 Tier-1 wiki fragments → anchored/sec-county-ma, each citing two independent evidence types (`f:dom=sec.gov` + `f:relay=jqp/allorigins`)"; cf. `DESIGN.md:64` Tier-1 definition ("multiple independent trace evidence types").
**Why it hurts:** Verified in `holdout_inferences.jsonl`: e.g. `dse~StartSeite@333` cites `f:dom=sec.gov` + `f:relay=allorigins`, both extracted from the same page's URL list (snippet shows `https://www.sec.gov/files/county.json` and the allorigins URL on the same page). One observation, two correlated features — not independent evidence types. The tiering is inflated by construction, and the target goal is the circular anchored one from #4.
**Fix:** Require Tier 1 evidence to come from distinct documents or observation types (e.g. URL evidence + jq-filter evidence from different records). Demote the 72 to Tier 2 and say so.

## 6. "All 400 traces → dsqa_250" is a sampling tautology
**Target:** `pug-research/goal-inference/REPORT.md` holdout table — traces: 400 Tier 2.
**Why it hurts:** The report admits "the sample is dominated by the DoE `zz=oai` cluster." Four hundred DoE-URL fragments matched the DoE question via the shared domain string (#3). This is not a holdout inference result; it is a description of the sample. A grader reads the table as "the matcher works on 400 real traces" — it didn't; it matched one domain 400 times.
**Fix:** Stratify the trace sample across domains before inferring, or move this row to a "sample composition check" footnote. Never let a single-cluster sample wear a results table.

## 7. The gems "correct negative" is abstention rebranded
**Target:** `pug-research/goal-inference/REPORT.md` — "618 gems → Tier 3 across the board… Correct negative: the taxonomy is eval-shaped and the gems are provider-shaped."
**Why it hurts:** The taxonomy is 900 eval questions; gem names/code cannot match it by construction. The matcher abstained. Calling abstention "correct" presumes the ground truth (gems have no goal in the taxonomy) that the experimental setup guarantees. Circular.
**Fix:** Call it abstention due to taxonomy gap, not a correct negative. A correct negative requires a case where a wrong goal was plausible and rejected.

## 8. goal-inference MODULE.md §4 is stale and contradicts the report
**Target:** `pug-research/goal-inference/MODULE.md:24,26` — "State: Design and method survey only. No matcher is implemented." / "Gap: No fragment-to-goal matcher exists."
**Why it hurts:** `match.py`, `REPORT.md`, `runs.md`, and three result files exist. The module doc violates the repo's own AGENTS.md §3 (update MODULE.md after verifying changes) and tells a grader the lane is vaporware.
**Fix:** Rewrite §4 to current state: matcher implemented in degraded mode, village validation now unblocked (data landed), open-set discovery still pending.

## 9. The "marked as superseded" degenerate runs aren't marked
**Target:** `pug-research/stylometry/REPORT.md:86` ("the six degenerate runs remain in the log and MUST be ignored") and `pug-research/stylometry/MODULE.md:42` ("marked as superseded") vs `runs_log.jsonl` (78 rows, zero containing "superseded" or "degenerate").
**Why it hurts:** Both docs assert a marking that does not exist in the file. Anyone re-analyzing the log — including your own `compare.py` runs summary — silently includes six degenerate Delta=2.0 rows.
**Fix:** Add a `superseded: true` field (or status column) to the six rows today. Verify with grep before claiming it again.

## 10. No within-partition baseline; "closest pair" is uninterpretable
**Target:** `pug-research/stylometry/REPORT.md` headline matrix (bold = closest pair per method); `MODULE.md` §4 admits "No significance thresholds yet. Similarities are descriptive."
**Why it hurts:** Delta is z-scored against a 4-partition background — a background of four. Those Delta values are not comparable to any literary scale, and "evals vs gems Delta 0.607" means nothing without knowing what Delta a partition gets against *itself*. The standard control (split wiki in half; halves should beat every cross-partition pair) was never run. Bold in the matrix invites reading noise as signal.
**Fix:** Run split-half within-partition baselines for every method; report cross-partition numbers as deltas from the within-partition ceiling. Until then, unbold the matrix.

## 11. The traces partition includes analyst voice by design, and findings don't discount it
**Target:** `pug-research/stylometry/build_lexdb.py:98-124` (`iter_traces` docstring: "Text fields: source_url, query parameter names and values, analyst note") vs `REPORT.md` Finding 4 (traces vs wiki Spearman 0.382, "shared core").
**Why it hurts:** The report's caveat ("'eval' and 'agent' appear in 100% of sampled trace docs") is listed and then ignored: Finding 4's shared-core claim and the provider-marker counts are computed over the contaminated mixture with no clean-partition rerun. You cannot tell how much of the traces↔wiki overlap is agent behavior vs analyst annotation vocabulary.
**Fix:** Build a `traces-clean` partition (URL + params only, no `attribution.note`, no `tags`) and re-run Findings 3–4 on it. Report both.

## 12. The gems partition mixes signals against its own docstring
**Target:** `pug-research/stylometry/build_lexdb.py:75-80` ("The gem name is agent-chosen… Code files are mostly boilerplate. Names are the payload.") vs `REPORT.md` Finding 1 ("evals and gems share a style… formal technical register").
**Why it hurts:** Finding 1's function-word cosine (0.644) and char 4-gram cosine (0.448) are computed over a partition the builder itself says is mostly boilerplate. If the similarity is driven by boilerplate Ruby + English prose sharing "formal register," that is a statement about RubyGems scaffolding, not agent style. The report never tests which sub-signal drives it.
**Fix:** Split into `gems-names` vs `gems-code` partitions; re-run Finding 1 on each. If names alone don't reproduce it, retract the "style" interpretation.

## 13. AGENCIES/RELAYS encode the answer key and it's undisclosed
**Target:** `pug-research/goal-inference/match.py:60-73` — `AGENCIES = {"sec","doe","bea","cdc","fbi","doj","census","aihw","unctad","ihme",…}`, `RELAYS`, `TRADE_TERMS`.
**Why it hurts:** The structured-feature vocabulary is the hunt's incident list, hand-compiled from prior findings. Any holdout trace touching a known incident agency gets features; a trace from a *new* agency gets none. This is test-set-informed feature engineering — the feature extractor knows the answers. The report never discloses the lists' provenance.
**Fix:** Disclose that the feature vocabularies were compiled from prior hunt findings; freeze them with a version note; state explicitly that the matcher cannot discover goals outside this vocabulary (recall on novel agencies is unmeasured).

## 14. No score floor; weak absolute scores presented as matches
**Target:** `pug-research/goal-inference/REPORT.md` holdout inferences (top scores 0.18–0.31, margins 0.15–0.26).
**Why it hurts:** Every reported "match" is rank-1, but no minimum cosine is ever set. At cosine 0.184 with 900 candidates, rank-1 is expected by chance for *some* candidate on *some* fragment. Without a floor, the tiering grades ranking position, not evidence strength.
**Fix:** Set a minimum-score floor (and a minimum margin) for Tier 1/2; report how many current Tier 1/2 hits fall below it. Move sub-floor hits to Tier 3.

## 15. DESIGN.md forbids what the REPORT's header claims
**Target:** `pug-research/goal-inference/DESIGN.md:15` ("Interim work may use synthetic village-shape data for pipeline testing only. No interim result counts as validation.") vs `REPORT.md` section header "## Validation: leave-one-out over 900 eval questions".
**Why it hurts:** Same self-contradiction class as #2, one level up: the design doc explicitly withholds the word "validation" from interim work, and the report uses it as a section header. (Compounds with #2's invariant violation.)
**Fix:** Retitle to "## Pipeline check on labeled proxy (not validation per DESIGN.md:15)". One-line change.

## 16. "Seven methods" vs a six-column matrix
**Target:** `pug-research/stylometry/REPORT.md` ("78 runs… seven methods" / "closest pair on four of seven methods") vs the headline matrix's six columns.
**Why it hurts:** Small, but it's the kind of inconsistency a grader circles in red and then uses as license to doubt the big numbers. The seventh method (shared bigrams/trigrams) appears only in Finding 1's prose.
**Fix:** Add the shared-ngram column to the matrix or change every "seven" to "six."

## 17. Grammar MODULE claims numpy/scipy; the code is stdlib-only
**Target:** `pug-research/grammar-network/MODULE.md` §3 ("Graph code uses only numpy/scipy") vs `build_a.py:25-30` (imports gzip, json, math, re, sys, time — stdlib only; numpy/scipy aren't in the imports).
**Why it hurts:** Minor, but a grader who tries `pip install` on an offline VM (PyPI is unreachable per the repo's own notes) hits a wall your docs built. And if the code doesn't need numpy, claiming it does is pure drift.
**Fix:** Correct §3 to "standard library only" or add the actual numpy/scipy usage.

## 18. drop_top5's "distinctive" is undefined; the empty-fragment edge case is unhandled
**Target:** `pug-research/goal-inference/REPORT.md` validation table ("drop_top5 (5 most distinctive terms removed)") and the dsqa_691 note ("fragment emptied completely… scoring 0.0").
**Why it hurts:** "Most distinctive" by what measure — TF-IDF within the question set? Within the fragment? Undefined, so the 0.9956 isn't reproducible from the report. And an empty fragment "scoring 0.0" means there's no minimum-token guard — the pipeline silently scores vacuous inputs instead of refusing them.
**Fix:** Define the distinctiveness measure in `runs.md`; add a minimum-token guard (refuse/flag fragments under N tokens) in `match.py`.

## 19. "Village blocked" statements are now stale
**Target:** `pug-research/stylometry/REPORT.md` ("AI Village side is blocked on dataset access"), `pug-research/goal-inference/DESIGN.md:15`, `MODULE.md` §4 gaps.
**Why it hurts:** All five village tables have landed (`data/raw/`: chat 52M, memories 1.9G, goals, code 100M, computer-use 2.0G). Every "blocked" caveat is now misinformation that understates what the submission can claim — or lets a grader think the work wasn't finished.
**Fix:** Refresh the three files' status lines now that workers are unblocked; the one honest remaining gap is that village *results* aren't in yet, not access.

---

## What the reports get right (so the fixes land in the right place)

- The stylometry caveats section is genuinely honest (degenerate Delta runs disclosed, tokenizer `%`-stripping disclosed, analyst-note contamination disclosed). The problem is that the findings above it don't act on those caveats — disclosure without discounting.
- The goal-inference "Honest limits" section is accurate. The problem is the sections above it ("Validation," "Most convincing single inference") are written at one epistemic level higher than the limits allow.
- Bug #3 in the goal-inference report (features must be first-class, not rerank-only) is a real finding — but DESIGN.md:Honest-limits #3 already predicted it, so it's a confirmation, not a discovery. Cite the design doc.
