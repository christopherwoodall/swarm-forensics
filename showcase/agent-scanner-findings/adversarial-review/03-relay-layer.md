# 03. Relay-layer adversarial review

Review date: 2026-10-03, MST.
New public retrievals occurred on 2026-10-04, UTC.
Exact retrieval times appear in the support manifests.

## Verdict

**Relay references survive. The reported denominator, operation-wide dominance, and novelty claims do not.**

The verified ProWiki export contains **46,278 county URL-token occurrences** across cumulative revision bodies.[1]
Its insert/replace hunks contain **32,310 occurrences**, including **12,904 outer-host jqp occurrences**.[1]
The saved analysis and an independent streaming recount agree.
Neither count measures requests, successful retrievals, agents, or operations.

jqp is the largest outer-host category within this defined text corpus.
Its cumulative occurrence share is **36.920%**, not the claimed 45%.
Its unique normalized URL share is **46.554%**.
Deduplication therefore does not necessarily reduce its share.

The source inventory already names lemino, jqp, Hexlet AllOrigins, and generic CORS proxies.[2]
“Never inventoried” fails against that inventory itself.
“No infrastructure” remains an unsupported absolute.

## Claims under review

Read [brief item 3](../discord-brief-2026-10-03.md#3-the-shadow-relay-layer--agents-real-infrastructure-unmapped) as a claim source.
Read [matrix C6, C12, and C14](../claim-matrix-2026-10-03.md) the same way.
Neither document is independent evidence.

| Claim | Decision | Reason |
|---|---|---|
| jqp: 14,341 of 31,525 references | Not reproduced | Neither number matches the stated corpus under the tested rules. |
| allorigins.hexlet.app: 4,928 references | Not reproduced | Outer-host and embedded-string counts differ from this figure. |
| api.cors.lol: 480 references | Unsupported host attribution | The source labels 480 as a generic CORS-proxy category.[2] |
| lemino was never inventoried | Contradicted | The source table explicitly inventories 24 lemino instances.[2] |
| jqp was the dominant operational relay | Unsupported | Textual frequency does not measure network utilization. |
| The operation built no infrastructure | Unsupported | The inspected records cannot establish the complete infrastructure universe. |
| C12: toolkit-level linkage | Retain only as resemblance | Shared services and templates do not establish common control. |
| C14: skills explain these exact URLs | Unresolved | No reviewed record connects a named skill execution to these occurrences. |

## Corpus and counting contract

The source is `revisions.jsonl` inside `full-wiki-logs.zip`.
The public clone is pinned to `e152f85f9032a8e4a55dade4b7990defe5e138c9`.[1]
The ZIP member and cloned ProWiki file have identical SHA-256 hashes.

- ZIP SHA-256: `eb68aa12d26bf189d8bfc4ce47f4d8af66ae5ba7ebbadd429738297a3cbb25ae`.
- Member SHA-256: `60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793`.
- Scanned objects: **14,591 revision rows**.
- Matching objects: **4,961 revision/time pairs**.
- Matching occurrence dates: **2026-06-18 through 2026-06-22**, using source timestamps.

A reference means one extracted HTTP(S) token containing `county.json` after at most three percent-decodes.
It is a lexical match, not validation of the requested resource.
The tokenizer follows the published extractor's delimiter rule.
Quotes, pipes, braces, and backslashes can truncate a token.
The denominator includes direct URLs, wrappers, mirrors, nested strings, and malformed candidates with parseable hosts.

Normalization decodes HTML entities and removes terminal punctuation.
It lowercases scheme and host, removes fragments, and normalizes percent-triplet case.
It removes default ports and preserves query order, cache-busters, and embedded targets.
The independent implementation uses scheme-specific default ports.
That difference changes none of the checked headline counts.
Encoded hostnames remain separate outer-host spellings.
These are normalized lexical tokens, not guaranteed distinct network resources.

Outer-host categories assign each token once.
Embedded-host flags search the decoded token and can overlap.
Embedded flags do not establish actual relay traversal.

A source-object/time tuple means `(prowiki, rev_id, time)`.
It does not mean a page, session, author, or HTTP request.
Different host columns can share the same tuple.
The additional URL-tuple metric means `(prowiki, rev_id, time, normalized_url)`.

### Cumulative revision bodies

All values below come from the verified recount.[1]

| Metric | All matching tokens | jqp.vercel.app | allorigins.hexlet.app | api.cors.lol | platform.lemino.ai |
|---|---:|---:|---:|---:|---:|
| Raw token occurrences | 46,278 | 17,086 | 1,740 | 55 | 36 |
| Unique normalized tokens | 5,978 | 2,783 | 147 | 9 | 12 |
| Unique source-object/time tuples | 4,961 | 2,985 | 859 | 46 | 20 |
| Unique source-object/time/URL tuples | 44,460 | 16,864 | 1,629 | 55 | 36 |
| Embedded-host flags, overlapping | Not additive | 17,198 | 4,759 | 379 | 41 |

jqp's next-largest outer-host comparator is `www.sec.gov`, with 12,108 occurrences.
The jqp source-object coverage is 60.169%; this is not a mutually exclusive host share.

### Insert/replace hunks

The hunk pass counts only destination lines marked `insert` or `replace`.[1]

| Metric | All matching tokens | jqp.vercel.app | allorigins.hexlet.app | api.cors.lol | platform.lemino.ai |
|---|---:|---:|---:|---:|---:|
| Raw hunk occurrences | 32,310 | 12,904 | 955 | 43 | 27 |
| Unique normalized tokens | 5,978 | 2,783 | 147 | 9 | 12 |
| Unique source-object/time tuples | 4,164 | 2,354 | 593 | 34 | 16 |
| Unique source-object/time/URL tuples | 31,542 | 12,809 | 919 | 43 | 27 |

The hunk occurrence share for jqp is **39.938%**.
Cumulative bodies contain 13,968 more occurrences than hunks.
Of those extra occurrences, 4,182 have jqp as their outer host.
Inherited page text MUST NOT be counted as new propagation.

Replacement lines can retain existing URLs after unrelated text changes.
Thus, hunk occurrences are not necessarily new URL introductions.
A separate URL-multiset comparison against each declared base gives **31,663 positive multiplicity increases**.
That comparison gives **12,816 jqp increases**.
It also does not measure requests.

Three matching revisions lack published earlier bases.
Their hunks contain 19 county tokens.
These records cannot establish when those tokens first appeared.
All other non-null comparison bases exist in the export.

### Reconciliation with the published figures

The source documentation defines references as URL-string occurrences in selected ProWiki revision bodies.[2]
The selected bodies mention `regCF`, `us-ma-`, or `county.json`.[2]
Every matching token in this recount occurs in a body satisfying that eligibility rule.

Literal-only matching yields **46,244 occurrences**.
The published URL-output file independently contains **46,244 ProWiki county-token rows**.[37]
Its literal jqp outer-host count is **17,084**.
Percent decoding adds 34 tokens overall and two jqp tokens.
This reconciles the published output with the recount, not with the narrative table.

The narrative table's exact numeric rows sum to **44,980**, before its approximate rows.[2]
That sum exceeds its stated total, 31,525.
Nested classification could create overlap, but the table does not supply a reproducible reconciliation.
The table mixes host-specific rows and category rows.
Its 480 CORS-proxy instances MUST NOT be reassigned wholesale to `api.cors.lol`.

Literal-only hunk URL-tuples total 31,521, not 31,525.
Numerical proximity does not identify the original denominator.
No tested rule reproduces 14,341 jqp occurrences.
The ratio 14,341 / 31,525 is 45.491%; arithmetic does not validate its inputs.

`briefdump-2026-10-03.zip` was not found anywhere under the task repository.
The original count script, corpus version, or omitted filter remains unresolved.
Do not retain the published figures as verified measurements.

## Historical endpoint evidence

The CDX checks used public GET requests with `matchType=prefix` and no collapse.
Each query covered 2026-01-01 through 2026-06-18, with a 1,000-row limit.
All returned fewer than the limit.
The queries differ from the malformed, unused legacy ledger entries 15–18.

| Endpoint | Historical observation | What it establishes |
|---|---|---|
| jqp.vercel.app | One CDX row. `/api/v0`, 2026-05-26T18:44:22Z, status 200.[19] | The endpoint was observed before the county burst. No target body was inspected. |
| allorigins.hexlet.app | 61 CDX rows. Earliest: 2026-05-11T18:12:47Z, `/get`, status 200.[20] | Historical service presence. The set contains 31 status-200 rows, plus failures. |
| api.cors.lol | 101 CDX rows. Earliest: 2026-01-02T04:58:32Z, status 404.[21] | Historical host presence. The set contains 22 status-200 and 46 status-429 rows. |
| platform.lemino.ai | No CDX rows within this query.[22] | No archive confirmation from this query; not evidence of absence. |

The first lemino county reference is `dse~AgentTmpOpenAIJun18Test@1`, at 2026-06-18T16:47:09Z.[1]
This establishes a dated reference, not a successful service response.
The reviewed CDX originals contain no decoded `county.json` matches.
Therefore, no county-response replay candidate existed within these bounded results.

### Public project identity and access conditions

Project namespaces below identify public source projects, not verified legal operators.
No human identity investigation was performed.

**jqp.** The public project is `sighrobot/jqp`, created in 2022.[26]
The inspected source commit predates June 2026.[31]
Its documentation describes a generic, free JSON/CSV filtering proxy.[32]
Its GET handler accepts a caller-supplied URL and contains no application-key check.[33]
That source does not prove the deployed configuration during the incident.
Its generic design and earlier capture oppose an incident-specific deployment claim.

**Hexlet AllOrigins.** The public project is `Hexlet/hexlet-allorigins`.[34]
Its 2022 documentation explicitly identifies the upstream AllOrigins fork.[30][34]
It documents caller-supplied targets and no-key usage examples.[34]
Those examples do not establish historical quotas, target restrictions, or every deployment access condition.
“Shadow clone” adds an unsupported concealment inference.
The claimed zero Shodan footprint was not independently reproduced.

**cors.lol.** The public project is `BradPerbs/cors.lol`, created in 2024.[28]
The inspected source commit is dated 2026-05-01.[29]
It documents a generic free proxy, not an incident-specific service.[35]
The source accepts a caller-supplied target without an application-key check.[36]
It also defines 20 requests per five minutes per IP.[36]
Historical 429 responses further oppose the phrase “wide-open” if that implies unrestricted access.[21]
The claimed historical Hetzner subnet was not independently validated.

**Lemino.** Current branding identifies a URL-to-Markdown service.[7]
The current page says “API Key (Optional for Demo).”[7]
This does not establish June authentication conditions, unrestricted targets, or deployment ownership.
No historical response body or dated service implementation was recovered for this endpoint.
Its June reference remains weaker evidence than the other endpoints' archive observations.

### Returned bodies versus status codes

Three existing urlquery reports submit Hexlet URLs containing `county.json`.[11][12][25]
Their request records do not supply a validated county dataset body.

- Report `830d0a0c-d9d4-483d-9149-c33c35bf2f84` records status 200 at 06:48:42.004Z on June 18.[11]
  Its 174,072-byte record has a Mozilla JSON-viewer MIME type and no available body.[11]
  A second JSON record has size zero.[11]
- Report `eb91d8ad-2f82-40df-803f-5474539757c1` records a blank response status and zero bytes.[12]
- Report `a9d4b7db-2921-40d9-aa1b-01d6927b9731` includes a 147,840-byte JSON-viewer record.[25]
  That body is unavailable; its other JSON record has zero bytes.[25]

These records support historical submitted URLs and response metadata.
They do not verify dataset correctness, origin contact, or target access authorization.
No relay was queried with an incident target during this review.

## Purpose, automation, and novelty

The corpus labels include “Filtered county JSON from SEC map” and “County conversion.”[1]
These labels support intended filtering and conversion, not confirmed execution.
The existing source analysis already describes multi-proxy probe templates and content-fetching infrastructure.[38]

The recount finds 2,740 jqp tokens containing the decoded Hexlet hostname.
It finds 324 jqp tokens containing `api.cors.lol`.
These are nested-string observations, not independently observed network hops.

| Proposed purpose | Evidence status |
|---|---|
| JSON filtering | Supported as intended use by labels and jq parameters. Execution remains unverified. |
| Markdown conversion | Supported as intended use by labels and wrapper selection. |
| CORS bypass | Supported as generic service capability. Specific browser-policy failures remain unproven. |
| Retry or fallback | Compatible with repeated targets and variant templates. Attempts cannot be counted from pasted alternatives. |
| Request laundering or egress | Plausible interpretation only. No demonstrated trust-boundary crossing follows from these strings alone. |
| Archive generation | Not established for these relay references. Do not import C14's generic recipe as execution evidence. |

No reviewed artifact identifies a common tool that automatically generated these exact occurrences.
Template generation, copied suggestions, and independent use of public documentation remain credible alternatives.
Repeated wrappers cannot identify agents or establish coordination.

C12's demotion MUST apply consistently to C6.
The same public relay can serve unrelated tasks.
C14 supplies a possible recipe, not a causal bridge between these records.
The source table already names lemino and the other relays.[2]
Its pinned commit date is not proof of its first public publication date.
A universal novelty claim nevertheless fails against the retrieved inventory.

Absence of a certificate burst cannot establish that no infrastructure was built.
“No incident-specific infrastructure was identified in this inspected subset” is the defensible limit.

## Recommended replacement

> The reviewed ProWiki export contains repeated references to pre-existing relay projects.
> jqp is the largest outer-host category among county-matching tokens in cumulative revision bodies.
> It accounts for 17,086 of 46,278 occurrences, or 36.920%.
> Insert/replace hunks contain 12,904 jqp occurrences among 32,310 county-matching occurrences.
> These are textual counts, not request or success counts.
> Lemino was already listed in the source inventory.
> No incident-specific infrastructure was identified in this inspected subset.
> The evidence does not establish a single operation or an exhaustive infrastructure census.

## Evidence files and checks

- [Saved recount](./_support/relay/counts.json).
- [Independent recount and base comparisons](./_support/relay/independent-recount.json).
- [Published-count reconciliation](./_support/relay/count-reconciliation.json).
- [Historical metadata and exact retrieval times](./_support/relay/historical-evidence.json).
- [Body-evidence checks](./_support/relay/body-evidence-check.json).
- [Project-source manifest](./_support/relay/project-source-manifest.json).
- [Documentation retrieval manifest](./_support/relay/documentation-manifest.json).
- [Durable source excerpts](./_support/relay/source-excerpts.md).
- [Source-to-evidence manifest](./_support/relay/source-evidence-manifest.json).
- [Citation ledger](./_support/relay/citation-ledger.json).
- [Verification results and coverage limits](./_support/relay/verification.json).

The existing count script was rerun without modification.
The independent pass streamed the cloned export without importing recovered corpus code.
Hunk bounds, hunk overlap, declared line counts, and comparison-base availability were checked.
Raw public responses remain under ignored `data/raw/relay-review/`.
The recovered public clone remains under ignored `data/raw/relay-wikiagents/`.
Its original retrieval time was not saved; this review records its verification time instead.

Reproduce the saved recount from the repository root:

```sh
make review-relay-count
```

The parent integration added this target without changing the counting algorithm.
Repository checks passed: `make test` ran 189 tests; `make lint` passed.
Remaining blockers are the missing briefdump, unreconciled original table, and unavailable historical target bodies.
The parent review owns the README and source guide.

## Sources

[1] https://github.com/joshuadavid/wikiagentswarminvestigation/tree/e152f85f9032a8e4a55dade4b7990defe5e138c9/agent-logs/prowiki
[2] https://github.com/joshuadavid/wikiagentswarminvestigation/blob/e152f85f9032a8e4a55dade4b7990defe5e138c9/tasks/sec-regcf-ma-cache/data-files.md
[7] https://platform.lemino.ai
[11] https://urlquery.net/report/830d0a0c-d9d4-483d-9149-c33c35bf2f84/json
[12] https://urlquery.net/report/eb91d8ad-2f82-40df-803f-5474539757c1/json
[19] https://web.archive.org/cdx/search/cdx?url=jqp.vercel.app%2Fapi%2Fv0&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000
[20] https://web.archive.org/cdx/search/cdx?url=allorigins.hexlet.app&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000
[21] https://web.archive.org/cdx/search/cdx?url=api.cors.lol&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000
[22] https://web.archive.org/cdx/search/cdx?url=platform.lemino.ai&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000
[25] https://urlquery.net/report/a9d4b7db-2921-40d9-aa1b-01d6927b9731/json
[26] https://api.github.com/repos/sighrobot/jqp
[28] https://api.github.com/repos/BradPerbs/cors.lol
[29] https://api.github.com/repos/BradPerbs/cors.lol/commits?until=2026-06-18T00%3A00%3A00Z&per_page=1
[30] https://api.github.com/repos/Hexlet/hexlet-allorigins/commits/84f7651c642cef788564b4dd285a274b53bde9e4
[31] https://api.github.com/repos/sighrobot/jqp/commits?until=2026-06-18T00%3A00%3A00Z&per_page=1
[32] https://raw.githubusercontent.com/sighrobot/jqp/9d3e86787f551b5609e36fec3e6ce73e255e5149/README.md
[33] https://raw.githubusercontent.com/sighrobot/jqp/9d3e86787f551b5609e36fec3e6ce73e255e5149/app/api/v0/route.js
[34] https://raw.githubusercontent.com/Hexlet/hexlet-allorigins/84f7651c642cef788564b4dd285a274b53bde9e4/README.md
[35] https://raw.githubusercontent.com/BradPerbs/cors.lol/4f8fd6f41ffd9e7a55f68ecd6d032474637ebe94/README.md
[36] https://raw.githubusercontent.com/BradPerbs/cors.lol/4f8fd6f41ffd9e7a55f68ecd6d032474637ebe94/main.go
[37] https://github.com/joshuadavid/wikiagentswarminvestigation/blob/e152f85f9032a8e4a55dade4b7990defe5e138c9/analyses/urls/outputs/urls.jsonl
[38] https://github.com/joshuadavid/wikiagentswarminvestigation/blob/e152f85f9032a8e4a55dade4b7990defe5e138c9/tasks/url-fetch-proxy-usage/README.md
