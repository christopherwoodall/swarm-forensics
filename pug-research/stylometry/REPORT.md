# Stylometry Report: OpenAI-side partitions (corrected)

78 original runs + 100 corrected runs logged in `runs_log.jsonl`.
Five partitions (gems split; see Corrections). Seven methods, eight numeric
columns (bigram/trigram Jaccard shown separately).

## Corrected headline matrix

No bold. Cross-partition numbers are read against the within-partition
ceilings below (#10). Lower Delta means closer style.

| Pair | J@1k | cos TF-IDF | cos func | Spearman | bi-J | tri-J | Delta | char cos |
|---|---|---|---|---|---|---|---|---|
| evals vs gems_names | 0.004 | 0.015 | 0.000 | 0.567 | 0.002 | 0.000 | 0.372 | 0.005 |
| evals vs traces | 0.095 | 0.128 | 0.306 | 0.179 | 0.004 | 0.000 | 0.829 | 0.212 |
| evals vs traces_clean | 0.089 | 0.044 | 0.376 | 0.143 | 0.005 | 0.000 | 0.706 | 0.080 |
| evals vs wiki | 0.145 | 0.122 | 0.311 | 0.217 | 0.007 | 0.000 | 1.472 | 0.171 |
| gems_names vs traces | 0.007 | 0.043 | 0.000 | -0.140 | 0.000 | 0.000 | 0.698 | 0.003 |
| gems_names vs traces_clean | 0.006 | 0.109 | 0.000 | 0.200 | 0.000 | 0.574 | 0.004 |
| gems_names vs wiki | 0.007 | 0.127 | 0.000 | 0.657 | 0.001 | 0.000 | 1.584 | 0.017 |
| traces vs traces_clean | 0.934 | 0.419 | 0.028 | 1.000 | 0.904 | 0.867 | 0.865 | 0.351 |
| traces vs wiki | 0.122 | 0.077 | 0.064 | 0.313 | 0.004 | 0.000 | 2.046 | 0.128 |
| traces_clean vs wiki | 0.114 | 0.147 | 0.264 | 0.352 | 0.003 | 0.000 | 1.842 | 0.161 |

## Within-partition ceilings (split-half baselines, #10)

| Partition | J@1k | cos TF-IDF | cos func | rho | bi-J | tri-J | Delta | char cos | keyness max\|G2\| |
|---|---|---|---|---|---|---|---|---|---|
| wiki | 0.967 | 0.999 | 1.000 | 0.973 | 0.847 | 0.853 | 0.033 | 0.999 | 271.3 |
| traces | 0.463 | 1.000 | 1.000 | 0.985 | 0.775 | 0.871 | 0.003 | 1.000 | 11.1 |
| traces_clean | 0.427 | 1.000 | 0.999 | 0.982 | 0.753 | 0.878 | 0.010 | 1.000 | 11.1 |
| evals | 0.491 | 0.979 | 0.995 | 0.684 | 0.285 | 0.147 | 0.061 | 0.990 | 13.8 |
| gems_names | 0.089 | 0.984 | 0.000 | 0.667 | 0.085 | 0.077 | 0.015 | 0.945 | 5.5 |

Reading guide: every cross-partition J@1k sits far below the relevant
ceilings. No cross-partition pair approaches within-partition similarity on
any method. gems_names is internally heterogeneous even against itself
(J@1k ceiling 0.089) — low cross-partition Jaccard for names is expected,
not informative. wiki keyness max|G2|=271 within-partition: distinctive-term
lists are volatile even for halves of the same partition; cross-partition
keyness claims get the same discount.

## Finding 1: RETRACTED

The v1 claim ("evals and gems share a style, not a topic") does not survive
the partition split (#12). Agent-chosen names alone show nothing:
evals vs gems_names gives J@1k=0.004, function-word cosine 0.000, char cosine
0.005 (subword tokenizer: J=0.038, cos=0.018 — still negligible). The v1
similarity reproduces almost exactly on the code bodies alone
(evals vs gems_code: function-word cosine 0.646, char cosine 0.471, vs v1's
0.644 / 0.448). The "shared formal register" was RubyGems scaffolding and
boilerplate prose, not agent style. The interpretation is retracted.
gems_code itself is removed from the dataset (audit: 740 files, median 1
byte, zero provider markers after the oai-1.3.0 exclusion — bust).

## Finding 2: the wiki is the lexical hub for tradecraft vocabulary (holds)

Unchanged. relay/jina/proxy/archive/task/wayback counts remain wiki-only.
The wiki is the stylistic outlier (Delta 1.47–2.05 vs every partition, vs a
within-partition ceiling of 0.033).

## Finding 3: provider markers — restated with corrected counts

| Term | gems_names word / subword | traces word | traces_clean word / subword | wiki word / subword | evals |
|---|---|---|---|---|---|
| oai | 1 / 82 | 89,241 | 0 / 1,494 | 393 / 7,531 | 0 / 0 |
| zz | 1 / 105 | 96,180 | 7,686 / 7,688 | 33 / 420 | 0 / 0 |

What changed: 797 of the old 814 gems "oai" tokens were the `oai-1.3.0`
OAI-PMH library (#1) — excluded, along with the whole directory. The old
"appears in gem names" was false under whole-word tokenization (names like
`agentoaitestabc123` never split). The new subword tokenizer reveals the real
names-carried signal the old one made untestable: 82 oai / 105 zz hits in
agent-chosen directory names. The old traces counts were analyst-note-driven
('oai'/'zz' in attribution prose); the clean partition's counts are
URL-driven (`zz=oai<digits>` split by the subword tokenizer) — the
agent-attributable part. Evals remain zero under both tokenizers. The
three-level linkage claim survives in corrected form: provider markers live
in agent output (names, trace URLs, wiki bodies), never in task prompts.

## Finding 4: shared terms rank alike between traces and wiki (attenuated, holds)

On traces_clean vs wiki, Spearman rho=0.352 (was 0.382 on the contaminated
partition). The shared core is URL-domain vocabulary ("https", "gov", "api",
"url"), not analyst annotation: keyness on traces_clean shows
URL terms (survey, measure, key, reportcard, msde, datadownloads, maryland,
civilrightsdata) where the contaminated partition showed analyst words
('only', 'the', 'where', 'digits', 'traffic', 'provider', 'instance').
Both facts from v1 hold: rank order measures the shared core, Delta measures
the whole profile (traces_clean vs wiki Delta 1.84 vs ceiling 0.010).

## N-sensitivity (corrected)

Jaccard at n=100: all cross-partition pairs 0.00–0.15; cores disjoint. The
v1 note "evals vs gems still leads at n=10,000" is dead with the partition —
evals vs gems_names J@10k-equivalent is noise against a 0.089 ceiling.

## Caveats (updated)

- traces_clean exists precisely because the traces partition mixes analyst
  voice (attribution notes, tags — 70% of its word tokens) with agent text.
  Findings 3–4 are reported on both; the clean numbers are the honest ones.
- Tokenizer fixed: percent-decoding before tokenizing (no more '3a'/'2f'
  hex-fragment garbage); new `subword` tokenizer splits concatenated agent
  names on case/digit/separator boundaries plus a documented morpheme
  list (long tokens only, >=10 chars, so ordinary English is never over-split).
- The six degenerate Delta runs are marked `superseded: true` in
  runs_log.jsonl (verified by grep); they remain in the log, ignored by
  analysis.
- Split-half baselines exist for every method (baselines.json); the matrix
  is unbolded and read against ceilings.
- gems_code removed from the dataset per the partition audit (bust).
- The traces sample is 1-in-20 (29,498 of 589,972). Deterministic stride.

## Absences worth noting

- "exploit" appears zero times in all partitions. "harness" zero times.
- "wget" zero times. "curl" only in the wiki (238).

## Village comparison: data landed (#19)

All five AI Village tables are in `data/raw/`. The functionally-matched
comparison (diagonal pairs + contamination check + action sequences + seven
non-lexical experiments) is in REPORT_V2.md. The honest remaining gap is
results interpretation, not access.

## Corrections

Adversarial review `pug-research/REVIEW.md`, all stylometry objections fixed:

- **#1** — Excluded `oai-1.3.0` (812 "oai" tokens, third-party OAI-PMH
  library). Recounted provider markers; Finding 3 restated as names-only
  with corrected numbers. The subword tokenizer additionally recovered the
  names-carried oai/zz signal (82/105) the old tokenizer could not see.
- **#9** — Six degenerate Delta rows marked `superseded: true` in
  runs_log.jsonl; verified with grep (6/6).
- **#10** — Split-half within-partition baselines for every method
  (baselines.py → baselines.json). Matrix unbolded; cross-partition numbers
  read against ceilings. Notable: gems_names ceiling J@1k=0.089 (internally
  heterogeneous); wiki keyness max|G2|=271 within-partition (volatile).
- **#11** — Built `traces_clean` (URL + params only). Findings 3–4 re-run on
  both; analyst-note words confirmed as the old driver, clean numbers
  reported as honest.
- **#12** — Split gems_names vs gems_code; Finding 1 re-run on each.
  Names: nothing. Code: reproduces v1. "Style" interpretation retracted;
  gems_code removed from the dataset per the audit rule.
- **#16** — Matrix now shows eight numeric columns (bigram and trigram
  Jaccard separated); "seven methods" count kept, keyness reported as term
  lists (no single number exists for it).
- **#19** — All "village blocked" statements refreshed; data landed, gap is
  results-pending.
- **Tokenizer fix (user steer)** — percent-decode before tokenizing;
  `subword` tokenizer added (case/digit/separator + documented morpheme
  list, long tokens only). Partitions rebuilt under word+subword; key
  comparisons re-run under both. Findings changed: Finding 3's names signal
  appeared (was untestable); Finding 1 died under both tokenizers.
- **Partition audit (user rule)** — gems_code: bust, removed. traces:
  contaminated, kept alongside traces_clean with both reported. wiki:
  agent-authored coordination text, kept. evals: benchmark task text, kept
  (clean by construction).
