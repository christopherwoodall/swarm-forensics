# Experiment Journal — SwarmTracers Hackathon, pug-research

Chronological lab journal. Newest entries at the bottom. Every entry states
what was tried, WHY it was tried, what resulted, and what was decided next.
Dead ends are recorded with the reason they died. Times are UTC; the work
happened the evening of 2026-10-03 US Central (2026-10-04 UTC), against a
hackathon deadline of 2026-10-04 17:00 Pacific.

Standing constraints for the whole program: nothing is committed or pushed
until the user says so (branch `pug-scratch`); holdout goal labels are
hypotheses supported by trace evidence, never ground truth; raw data stays
untracked under `data/raw/`; scripts are standard-library only (no PyPI on
this VM); large files are streamed, never loaded whole.

---

## 2026-10-04 ~02:30 — Program kickoff and lane design

**What:** Stood up the hackathon submission scaffold in
`christopherwoodall/swarm-forensics` on branch `pug-scratch`, work under
`pug-research/`.

**Why:** The user framed the submission as three questions: (1) do the
OpenAI-associated public trace collections share lexical patterns with AI
Village agent data (stylometry); (2) can end-state goals be inferred from
fragments, using Village tasks as labeled data and the OpenAI traces as an
unlabeled holdout (goal inference); (3) can the incident hunt be turned into
a repeatable detection framework (the 5Ws, already committed in
silent-locus). The user explicitly directed: document all steps and
rationale; experiment freely; multiple runs are OK; keep collection sets
separate (gems-like, urlquery-like) rather than one merged corpus; split AI
Village by task; use the OpenAI set as a holdout since their prompts are
unobservable but their goals are inferable.

**Decided:** Three lanes — `pug-research/stylometry/`,
`pug-research/goal-inference/`, `pug-research/grammar-network/` (added
later). Repo conventions adopted: root Makefile is the command entry point,
one MODULE.md per subsystem, raw data untracked.

---

## 2026-10-04 ~02:45 — Stylometry v1: partition design

**What:** Built `build_lexdb.py`, partitioning the OpenAI-side evidence
into four separate collections: `gems` (618 gem directories, names + code),
`traces` (29,498 records, deterministic 1-in-20 stride of the trace
corpus), `wiki` (14,591 collusion-wiki revision bodies), `evals` (900
DeepSearchQA questions).

**Why separate:** The user wanted collection sets kept distinct
("resemble gems, urlquery, etc"). Merging them would have smeared the
provider-level vs task-level vs instance-level signals the hunt's
three-level linkage model needs to distinguish.

**Dead ends / exclusions:** `pages.jsonl` excluded — it duplicates revision
content already in the wiki partition (double counting). Marker-sweep
events excluded — they contain analyst prose, not agent text, and would
have contaminated the "agent voice" partitions. Both exclusions are logged
in the lane MODULE.md.

---

## 2026-10-04 ~03:15 — Stylometry v1: 78 runs, seven methods

**What:** Ran the full pairwise matrix (4 partitions, 6 pairs) with seven
methods: Jaccard at multiple cutoffs, TF-IDF cosine, function-word cosine,
Spearman rank correlation, log-likelihood keyness, shared bigrams/trigrams,
Burrows Delta, character 4-gram cosine. All 78 runs in `runs_log.jsonl`.

**Why seven methods:** No single similarity measure is trustworthy on this
data (URL-heavy, code-mixed, analyst-contaminated). Convergence across
methods is the finding; any single number is noise.

**Dead end:** The first six Burrows Delta runs were degenerate — Delta came
out 2.0 for every pair. Cause: z-scoring against only the two profiles
being compared collapses the statistic. Fix: z-score against the
four-partition background and re-run. The six bad runs remain in the log,
marked superseded, so nobody re-discovers them.

---

## 2026-10-04 ~03:20 — Stylometry v1 findings (REPORT.md)

**What the numbers said:**

1. **evals ↔ gems closest on four of seven methods** (function-word cosine
   0.644, character cosine 0.448, Delta 0.607). Keyness showed this is
   shared formal/technical register, not shared topic or tradecraft —
   eval-distinctive terms are question prose ("according", "which",
   "states"), gem-distinctive terms are Ruby code ("end", "def", "class").
2. **The wiki is the tradecraft lexical hub**: `relay` 13,422 / `jina`
   3,545 / `proxy` 1,778 / `task` 26,368 — nearly all in wiki, near zero
   elsewhere. But it is also the stylistic outlier (Delta 1.8–2.0 vs every
   other partition). Its distinctive terms are URL-encoding fragments
   ("3a", "2f") because the tokenizer strips "%" — a known inflation
   artifact, recorded as a caveat.
3. **Provider markers link gems/traces/wiki, never evals**: `oai` appears
   814 / 89,241 / 393 times; `zz` 1 / 96,179 / 32; both zero in evals.
   Eval questions are task text and carry no harness bookkeeping. This is
   the three-level linkage model (provider vs eval/task vs agent-instance)
   showing up in the bytes.
4. **traces ↔ wiki: Spearman rho highest (0.382) while Delta calls them
   farthest (1.996).** Both true: shared terms keep similar rank order
   (both are URL-heavy), but the full profiles diverge on their large
   distinctive tails. Rank order measures the shared core; Delta measures
   the whole profile.
5. **Cores are disjoint**: Jaccard@100 scores 0.04–0.15 across all pairs.

**Honest limits recorded:** the traces partition leaks analyst metadata
("eval", "agent" in 100% of sampled docs — not agent voice); the traces
sample is 1-in-20; "exploit", "harness", "wget" appear zero times anywhere.

**Why this mattered:** Bag-of-words hit its explanatory limit here. The
partitions are lexically divergent with disjoint cores. That negative
result is what motivated the grammar-network lane (structure instead of
words) and the apples-to-apples re-partition (match by communicative
function, not by corpus).

---

## 2026-10-04 ~03:10 — Goal-inference lane: degraded stack decision

**What:** Wrote SOTA.md (bi-encoder retrieval + cross-encoder reranking as
the recommended architecture), DESIGN.md, then implemented `match.py` as an
explicitly degraded baseline: TF-IDF cosine with structured features as
first-class stage-1 dimensions, plus a transparent heuristic rerank
(0.6·cosine + 0.4·type-weighted feature coverage).

**Why degraded:** This VM has no sentence-transformers, no torch, and no
usable PyPI. Rather than fake the SOTA stack, the lane runs a transparent
baseline and documents the gap. The report states plainly: do not cite
these numbers as SOTA-stack results.

**Why structured features:** Non-linguistic fragments (URLs, query params,
jq filters) carry goal signal that text embeddings miss. Feature families:
domain, parameter, path, jq operation, filter value, relay, agency, year.

**Key design finding:** When structured features were rerank-only, word
noise beat them — dsqa_250 ranked 41st on words alone for its own DoE
traces, so the rerank shortlist never contained it. Promoting features to
first-class stage-1 dimensions fixed it. This is now a design rule, not a
tuning detail: structured trace evidence must be a stage-1 citizen.

**Bugs found and fixed:** (1) the year regex used the match group instead
of the full match, so every year became `f:year=20`; (2) `www.sec.gov`
mismatched bare `sec.gov` — hosts now normalized at extraction; (3) the
first rerank was too weak to matter (see above).

---

## 2026-10-04 ~03:21 — Goal-inference validation and anchored checks

**What:** Leave-one-out over the 900 eval questions: top-1 1.0000 on
stride-degraded fragments, 0.9956 with the 5 most distinctive terms
removed (top-3 0.9967). Anchored checks on real trace fragments: a bare
DoE API trace (no prose) recovered dsqa_250 — the hunt's one confirmed
eval link, independently re-derived from the URL alone; a Massachusetts
county jq-filter fragment recovered the anchored goal `sec-county-ma` at
0.76 cosine, on jq/filter/relay evidence.

**Why these checks:** LOO measures pipeline health; the anchored checks
measure whether the pipeline works on real incident fragments. The DoE
check is the one with teeth: it reproduced the hardest-won attribution in
the hunt from a bare URL.

**Honest reading recorded:** LOO measures same-distribution fragment
recovery, NOT agent-query→goal transfer. The 7 misses are all same-family
confusions (election→election) — the correct failure mode for goal
inference. One degenerate case: dsqa_691's fragment emptied completely
after top-5 removal (short question) — short fragments need a
minimum-token guard.

**Holdout run (1,418 fragments):** 400 traces → dsqa_250, Tier 2
(sample dominated by the DoE `zz=oai` cluster — do not generalize beyond
that sampling frame); 400 wiki → 72 Tier 1 (two independent evidence
types) + 320 Tier 2 + 8 Tier 3, the Tier-1s hitting `sec-county-ma`; 618
gems → all Tier 3, an honest negative (no goal-taxonomy coverage, recorded
as such).

---

## 2026-10-04 ~03:30 — AI Village acquisition saga

**What:** Downloaded the AI Village tables from the gated HuggingFace
dataset `aidigestorg/ai-village`. Final state: all five tables in
`pug-research/stylometry/data/raw/` — chat_messages (52M),
agent_memories (1.9G), agent_goals (4K), claude_code_messages (100M),
computer_use_turns (2.0G).

**Why it took three attempts:** The dataset is manually gated. The first
token 401'd on everything. After access review, the replacement token
downloaded 2 of 5 files (chat, memories) but 401'd consistently on the
other three — same token, same repo, not transient, not a storage-backend
difference. The user supplied a second token with broader grant, which
landed all five.

**Why curl, not the HF python library:** The VM's `huggingface_hub` is
broken (bundled httpx2 chokes on the environment's IPv6 NO_PROXY entries;
without proxies, egress fails TLS). curl handles the egress proxy fine.
This is now a standing tool note.

**Why these tables:** chat_messages (agent coordination voice),
agent_memories (long-horizon agent voice + distilled prompt content),
agent_goals (the labeled task backbone — only 33 rows, but they are the
only ground-truth goals in the program), claude_code_messages (code),
computer_use_turns (behavioral action logs — the best shape-match for our
URL/action traces).

---

## 2026-10-04 ~03:35 — Apples-to-apples re-partition (worker running)

**What:** The user directed: match the datasets by shape — compare apples
to apples. Rebuilding the lexdb along functional lines: wiki revisions ↔
chat_messages (agent speakers only — the ~10k user rows are dropped as
contamination); evals ↔ agent_goals (task statements); gems ↔
claude_code_messages (code); traces ↔ computer_use_turns (behavioral
traces); agent_memories as a village-only reference voice.

**Why:** The v1 partitions mixed communicative functions. If two corpora
share a harness, the similarity should appear between functionally matched
slices (coordination↔coordination, task↔task), not between arbitrary
corpus chunks.

**User priority:** the computer_use_turns ↔ traces pair is the one to push
hardest — both are action logs, and the harness fingerprint, if it exists,
lives in what-follows-what (action transitions, retry shapes), not in
vocabulary.

**Status:** worker running. REPORT_V2.md pending. It will also test the
agent-only chat filter both ways — if the user rows change the result,
that contamination effect is itself a finding.

---

## 2026-10-04 ~03:37 — Grammar-network lane: Build B (request grammar)

**What:** The user asked "what about the grammar network". Two builds were
proposed and approved: (A) syntactic co-occurrence networks per partition
— graph metrics instead of shared words, testing structural convergence
where bag-of-words found divergence; (B) the request-construction grammar
as a graph — nonce templates, relay chains, path/param grammars — the
toolkit fingerprint that stays constant while tasks change. The user added:
expand both, and include text found inside source code (gem strings and
comments became their own `gems-code-nl` partition).

**Build B results (51,674 requests, REPORT.md):**

- **Layering grammar:** requests nest proxies in a consistent
  outer→inner order — jq/server-side extraction outermost (jqp),
  render/CORS relays in the middle (md.succ.ai, allorigins, r.jina.ai),
  target innermost (sec.gov, investor.gov). The nesting order is invariant
  across 242 observed chains even though the relay inventory churns.
- **New relay surfaces** not in the prior hunt inventory: markdown-render
  proxies (md.succ.ai 1,516 refs, markdown.new 539, pure.md; 11,600
  md-wrapped URLs in wiki), personalized Cloudflare worker CORS proxies,
  webcrawlerapi.com as an outer fetch layer, shortener vanderbi.lt inside
  chains.
- **New target families:** reportcard.msde.maryland.gov (14,353 refs,
  bulk school report-card downloads — a target family the incident map
  does not cover), api.datausa.io (OLAP API), wikiservice.at (the agents'
  own wiki fetched as a target), jsonhero.io as render proxy, Preservica
  archives via a worker proxy.
- **Template inventory:** `zz=oai<digits>` (747), literal `%26` (1,168,
  Census failure morphology), `?x=0.<digits>` SEC-burst nonce (rare here),
  doubled-scheme (AIHW-style malformation), `zzbulk`/`prepnonce` arquivo
  fuzz grammar (live).
- **jq as repeated program:** the MA-county extraction is not one report
  but a repeated extraction program (array slice + map + select with
  us-ma/usd/methodology filters — pulling metadata rows too).

**Fingerprint assessment:** usable. Three stable layers (provider tags,
relay grammar, target grammar); relay hosts churn, nesting order does not.

**Fallbacks recorded:** no POS tagger on the VM, so Build A uses windowed
co-occurrence — documented as a fallback, not equivalent to dependency
parsing. The traces URL-metadata partition is excluded from Build A prose
networks (non-linguistic; belongs to Build B).

**Status:** Build A results pending; Build B complete.

---

## 2026-10-04 ~03:45 — Pattern database + experiment diversity (user steering)

**What:** The user pushed back twice: first, "so few [experiments]...
maybe we don't need all SOTA — like, create a database and mine patterns";
then "More >>>" and "different diversity == gooood".

**Why this changed the program:** The lanes had depth in a few methods but
narrow breadth. The user's instinct: a well-built pattern database plus
plain frequency/conditional-probability mining beats a handful of clever
methods, and diverse experiment *kinds* (not just more runs) are what
separate or unite the partitions.

**Steered into the lanes:**

- **Grammar lane:** build `patterns.sqlite` — url_templates (normalized
  shapes with nonce slots), relay_chains (ordered host sequences),
  param_grammars (param sets per host/path), nonce_templates (regex
  shapes), action_ngrams — mined with plain counts and conditional
  probabilities. New `make patterns` target; PATTERNS.md pending.
- **Grammar lane, behavioral:** Markov transition matrices (order-1 and
  order-2) over action/host sequences per partition; retry-loop mining
  (A→X→A cycles); session-length distributions; first/last-action
  distributions; burstiness from inter-arrival times; failure vocabulary.
- **Stylometry lane, non-lexical style:** punctuation profiles, caps/digit
  density, sentence-length distributions, markdown-structure markers, URL
  density and embedding style, hedging-vs-assertive ratios, type-token
  ratio.
- **Goal lane, diagnostics:** feature-family ablations (lexical-only vs
  structured-only vs hybrid), per-family importance, village cross-task
  confusion matrix, prompt-element ablation (role vs mission vs
  guardrails), evidence-type breakdown on holdout inferences.

**Rationale for the diversity:** every one of these is a signal class that
bag-of-words and TF-IDF cannot see. If the harness is shared, it should
show up in several independent signal classes at once; if the partitions
are truly unrelated, the methods should disagree with each other.

---

## 2026-10-04 ~03:40 — Prompt inversion

**What:** The user noted the Village side also contains prompts and
configs — prompt→behavior pairs with ground truth on one side. Built
`invert.py` (`--mode {mine,map,invert,all}`, stdlib only): mine
prompt-like content from memories/goals, map prompt elements to behavior
markers, invert to the OpenAI holdout.

**Extraction rules:** streamed agent_memories (1-in-5 stride, recorded)
with line-level regexes over five element types (identity, mission,
guardrail, tool, schedule) plus agent_goals name+description as
task_framing. Only ~9% of sampled records use the standard
"Consolidated/Internal Memory" headers — section names vary freely, so
pattern families are used instead of section parsing. Trades recall for
precision, and says so.

**Key honest finding (before the run even finished):** the
village→holdout transfer is weak by construction — village prompts are
game roleplay ("Benevolent Prankster"); the OpenAI harness is eval-task
machinery. The learned within-village map therefore does NOT transfer.
Inversion instead proceeds from trace evidence against a fixed hypothesis
set (session-tag bookkeeping, relay-ladder tool use, gov-API retrieval
role, server-side filtering, nonce cache-busting, end-to-end retrieval
mission, no-evidenced-guardrails), tiered T1 (2+ independent evidence
types) → T2 (single) → T3 (speculative). Every output is a hypothesis.

**Status:** PROMPT_INVERSION.md written; Results section (section 5) empty
pending the run. `make invert` wired and waiting.

---

## 2026-10-04 ~03:42 — Makefile: recreation and per-lane ownership

**What:** The user demanded the whole program be recreatable from
makefiles, then refined: a Makefile in each research directory — one per
experiment lane.

**Why:** A grader (or future us) should reproduce every result with make
targets, not by re-reading chat history. Lane-local Makefiles keep each
experiment's interface next to its code; the root Makefile delegates.

**Done:** `pug-research/stylometry/Makefile`
(download/lexdb/lexdb-v2/compare/compare-v2/actions/all),
`pug-research/grammar-network/Makefile` (extract/a/b/all),
`pug-research/goal-inference/Makefile` (match/invert/all). Root keeps the
same public targets (`stylo-compare`, `goal-match`, `pug-all`, …) as thin
`make -C` wrappers. `make pug-all` runs download → stylometry → grammar →
goal inference end to end; all steps idempotent (skip what's done);
`HF_TOKEN` read from the environment, never hard-coded. Lane READMEs
updated (the goal-inference README still said "design only" — stale, now
fixed).

**Bug fixed along the way:** `--pair` was passed unquoted in the old root
target, which would have broken multi-word pairs; lane makefiles quote it.

---

## Pending as of this entry

1. **Apples-to-apples worker:** REPORT_V2.md — functionally-matched pairs,
   computer_use_turns ↔ traces prioritized, 7 non-lexical style
   experiments.
2. **Grammar worker:** Build A results; `patterns.sqlite` + PATTERNS.md;
   behavioral/sequential experiments (Markov, retry loops, burstiness).
3. **Prompt-inversion worker:** `invert.py` run results → PROMPT_INVERSION.md
   section 5; `make invert` end-to-end check.
4. **Journal:** re-scan lane dirs and append results as workers land.
5. **Before submission:** adversarial review of all lane reports for
   overclaiming; rotate the two chat-exposed tokens (GitHub PAT, HF
   tokens); cut the evidence packet. Nothing committed until the user says
   push.
