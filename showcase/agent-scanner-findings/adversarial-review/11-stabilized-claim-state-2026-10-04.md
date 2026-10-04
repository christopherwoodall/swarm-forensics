# 11 — Stabilized claim state

Status: Current authority map for `agent-scanner-findings`.
Recorded: 2026-10-04, local time.
Evidence retrievals include 2026-10-04 UTC.

This note stabilizes claim wording without rewriting earlier documents.
It adds no new source retrievals or historical observations.

## Authority map

| Layer | Authority | Rule |
| --- | --- | --- |
| Primary observation | Cited public sources and retained support records | Use the source guide to check each record's unit, scope, and limits. |
| Current adjudication | [Executive result](00-executive-result.md), [corrected claim ledger](09-corrected-claims.md), and focused chapters | Use these files for current claim wording and confidence. |
| Detailed evidence | [Source guide](SOURCE-GUIDE.md), chapter receipts, and `_support/` artifacts | Read the cited record before promoting an interpretation. |
| Historical claims | [Original brief](../discord-brief-2026-10-03.md), [claim matrix](../claim-matrix-2026-10-03.md), [earlier review](../adversarial-review-2026-10-03.md), and [review specification](../adversarial-review-spec.md) | Preserve these as inputs and prior hypotheses, not current evidence. |

The source guide maps source namespaces and evidence limits.
Citation numbers remain chapter-local.
Repeated sources do not become independent witnesses.
The mechanical verifier checks files and mappings, not causal conclusions.

When a later correction conflicts with an earlier claim, use the corrected ledger.
When a source does not resolve a conflict, retain the conflict as unresolved.
Do not silently harmonize competing snapshots.

## Current claim state

| Claim family | Current bounded statement | Do not assert | Evidence route |
| --- | --- | --- | --- |
| SEC archive burst | The current CDX query returns 63 entries, 62 URL keys, and 60 main-digest rows. Thirty-nine entries span 463 seconds. This is a level-1 action-shaped archival trace. | Do not assert an identified initiator, Save Page Now use, agent action, target request, or later agent use. | [SEC review](01-sec-wayback.md); [`cdx-events-redacted.csv`](_support/sec/cdx-events-redacted.csv) |
| SEC nonce grammar | The broad `?x=0.<digits>` family has 41 entries. Seven have exactly 17 digits. | Do not describe all 41 as exact 17-digit nonces or identify a generator. | [SEC review](01-sec-wayback.md) |
| Census, May 24 | Two matching browser reports contain malformed key-bearing requests that ended at `Missing Key`. This is the earliest matching trace in this bounded search. | Do not call May 24 the operation's start or claim successful data retrieval. | [Census review](04-census.md); [corrected ledger](09-corrected-claims.md) |
| Census, June 17 | Three separate archive wrappers preserve empty or error responses. Two independent archive copies contain the public static file. | Do not claim a chained relay or successful relay retrieval. The direct copies are not linked to those wrappers. | [Census review](04-census.md); [executive result, lines 15–20](00-executive-result.md) |
| AIHW, June 18 | One malformed Jina-wrapped URL was archived. Its replay contains a security-check page. | Do not claim the workbook was fetched, an agent initiated the capture, or this joins the later pharmaceutical task. | [AIHW review](05-aihw.md); [executive result, lines 22–26](00-executive-result.md) |
| Relay references | The pinned ProWiki export has 46,278 county URL-token occurrences in cumulative bodies and 32,310 in insert/replace hunks. Jqp accounts for 17,086 body occurrences and 12,904 hunk occurrences. | Do not call textual references traffic, successful fetches, agents, or operations. The old 14,341/31,525 figures remain unreproduced. | [Relay review](03-relay-layer.md); [`counts.json`](_support/relay/counts.json) |
| Cross-cluster linkage | Treat Census, AIHW, SEC Wayback, and SEC urlquery as related-looking but independent. No common operation is established. | Do not merge clusters from timing, shared services, common targets, or morphology alone. | [Linkage review](02-operation-linkage.md); [`operation-graph.json`](_support/operation-graph.json) |
| Dormancy | One scoped urlquery query returned no recent county-string matches. Other controls failed or access was unavailable. | Do not claim global silence, cessation, or confirmed dormancy. | [Dormancy review](06-dormancy-and-novelty.md); [feed tests](_support/novelty/feed-tests.jsonl) |
| Novelty | The bounded searches found no exact prior mention for some narrow observations. Broader relay and AIHW activity had prior coverage. | Do not claim universal novelty or absence from all publications. | [Dormancy and novelty review](06-dormancy-and-novelty.md); [search ledger](_support/novelty/search-ledger.jsonl) |

## Version conflicts and scope boundaries

| Conflict | Stabilized reading | Remaining state |
| --- | --- | --- |
| SEC: 65 entries and 61 digests versus 63 entries and 60 main-digest rows | Use the retained 63-row query for the focused review. | The missing brief dump and original response prevent snapshot reconciliation. |
| SEC: 14:52 first capture versus earlier timestamps | 14:52 is the first bare-decimal capture. The raw query includes earlier entries. | Different query populations explain some, but not all, historical wording. |
| SEC mechanism: earlier review calls 59 rows on-demand saves | The focused SEC chapter classifies only an action-shaped archive trace. | Capture method and initiator remain unknown. |
| SEC: 41 exact 17-digit values | Only seven entries match that exact grammar. | Corrected in the focused SEC chapter. |
| Relay: 14,341/31,525 and 45% operational share | Use the reproduced textual counts and explicit corpus denominator. | The published numeric table does not reconcile. |
| Operation: matrix C7 says “same operation”; C12 is demoted | Keep the clusters separate pending instance-level evidence. | The matrix retains incompatible language. |
| Dormancy: earlier matrix says three-feed confirmation | Retain only the bounded urlquery result. | URLScan controls failed; GreyNoise returned HTTP 401. |
| Census: earlier “successful triple-relay retrieval” | Retain three separate wrapper captures with empty or error responses. | No linked content-bearing relay response exists in the reviewed support. |
| Census replay bodies: the earlier review said status/body evidence was unavailable | The focused review preserves empty, error, and restriction responses. | These separate bodies do not establish a chained or successful retrieval. |

The missing `briefdump-2026-10-03.zip` prevents reconstruction of some original searches and counts.
Do not treat this missing source as proof that a historical event did not occur.
The focused review does not independently validate every later matrix lead.

| Matrix lead | Review boundary |
| --- | --- |
| C5, LAC | Not re-examined. |
| C8, NPWS | Unverified extension; no exact host or trace set was supplied. |
| C13, SwarmMemo | Unverified extension; exact post and provenance were not supplied. |
| C14, public skills | Unverified extension; named versions and the claimed file inventory were not supplied. |
| C15, apchem/tmcleod | Not re-investigated; the matrix's prior-publication attribution remains unverified here. |

These labels describe review coverage, not event truth.
An unverified extension is not a negative finding.

## Morphology-hunter boundary

Treat future morphology-hunter output as candidate observations, not adjudicated claims.
Each candidate MUST retain its source ID, raw reference, exact match, transformation steps, rule version, and counting unit.
Keep occurrence counts separate from distinct URLs, revisions, events, and actors.
A morphology match supports resemblance only.
It does not establish identity, transmission, successful retrieval, or causal dependence.
Upgrade a relation only when independent evidence supports access and later behavioral dependence.

## Update rule

Add new evidence with its retrieval time, query, source reference, and limitations.
Update the current wording only when that evidence changes a claim boundary.
Preserve earlier wording in this conflict register until its source is reconciled.
Do not edit original briefs or support records to make them match this note.
