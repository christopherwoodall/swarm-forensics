# Annotated source guide

## How to use this guide

Begin with the focused chapter for a claim.
Follow its numbered citation to the public source.
Then inspect the linked support receipt and its time, unit, hash, and limitation.

The [complete register](_support/source-catalog.md) maps all cited sources to retained evidence groups.
The [machine-readable manifest](_support/source-manifest.json) contains 87 distinct normalized public URLs.
Those are source records, not 87 independent observations or corroborating investigations.

Citation numbers are **chapter-local**.
The parent synthesis uses its own ledger.
Do not read a Census citation against the SEC ledger.

| Namespace | Applies to | Cited source IDs | Ledger |
| --- | --- | ---: | --- |
| `sec` | Chapter 01 | 12 | [SEC ledger](_support/sec/citation-ledger.json) |
| `relay` | Chapter 03 | 22 | [Relay ledger](_support/relay/citation-ledger.json) |
| `census-aihw` | Chapters 04–05 | 18 | [Census/AIHW ledger](_support/census-aihw/citation-ledger.json) |
| `novelty` | Chapter 06 | 38 | [Feed/publication ledger](_support/novelty/citations.json) |
| `parent` | Executive result and synthesis chapters | 18 | [Parent ledger](_support/parent-citations.json) |

The sums overlap because chapters reuse sources.
Unused provisional registrations are not promoted into cited findings.

## 1. Claim sources: evidence of what was asserted

- [Original brief](../discord-brief-2026-10-03.md): six headline claims, dated October 3.
- [Later claim matrix](../claim-matrix-2026-10-03.md): fifteen claim rows, including later demotions and new leads.
- [Review specification](../adversarial-review-spec.md): requested evidentiary tests and report structure.

These documents are not independent support for their own assertions.
The original brief contains an exposed credential indicator.
This review does not reproduce or validate it.
The missing `briefdump-2026-10-03.zip` prevents reconstruction of some original counting and search choices.

## 2. Wayback CDX: index-level observations

**Type:** public archival metadata.
**Useful for:** capture times, URL-key deduplication, digest groups, response classes, and narrow temporal controls.
**Not sufficient for:** capture initiator, Save Page Now mechanism, target receipt, or agent readership.

SEC's raw and collapsed queries are preserved in the [retrieval register](_support/sec/retrieval-table.md).
The [63-row table](_support/sec/cdx-events-redacted.csv) retains timestamps, hashes, digests, and response metadata.
The [counts](_support/sec/counts.json) retain controls and wiki-window comparisons.
Raw original URLs were not republished in this table.

Census and AIHW use exact query URLs in their case JSON files.
Their archive timestamps MUST remain distinct from unknown source-request times.

## 3. Raw archive replays: response-content evidence

**Type:** public archive response bodies, fetched through `id_` replay URLs.
**Useful for:** distinguishing an empty wrapper, a restriction page, a security-check page, and a data file.
**Limit:** historical response replay does not identify the original requesting actor.

Read [Census June 17 metadata](_support/census-aihw/census-june17-redacted.json).
It records three wrappers and two independent direct-file captures.
Read [AIHW metadata](_support/census-aihw/aihw-june18-redacted.json).
It records the malformed original, normalized urlkey, gzip handling, and decoded body hash.

The [bounded excerpts](_support/census-aihw/evidence-excerpts.md) preserve load-bearing response text.
The [parent replay check](_support/parent-replay-verification.json) independently matches four decoded hashes.
Raw parent replay bytes remain under ignored `data/raw/adversarial-review/parent-replays/`.

## 4. urlquery browser reports and exported HTTP entries

**Type:** browser-session report metadata and recorded HTTP transactions.
**Useful for:** submitted URLs, transaction timestamps, methods, redirects, status, and available response content.
**Limit:** a report is not an authenticated agent, and a remote peer IP is not the submitter's IP.

The [May 24 metadata](_support/census-aihw/census-may24-redacted.json) covers five Census-classified catalog reports.
Two match the brief's indicator; the other three are scoped controls.
Credential comparison occurred in memory.
The retained output records equality and parsing behavior without the credential value.

The US/Canada ZIP's SEC export supplies parent measurement M1.
See [parent-measurements.json](_support/parent-measurements.json) for exact member references and source hashes.
The exported county-substring set has 568 entries across 546 report IDs.
These quantities MUST NOT be called successful data fetches.

## 5. Wiki source export and published URL analysis

**Type:** released revision bodies, hunk metadata, and investigator-generated URL inventories.
**Useful for:** dated references, byte-level text comparisons, and denominator sensitivity.
**Limit:** cumulative revision bodies repeat inherited material; labels do not establish identities.

The source revision-member SHA-256 is pinned in the relay and SEC reports.
The relay review also pins the public repository commit.
Its [count file](_support/relay/counts.json) and [independent recount](_support/relay/independent-recount.json) distinguish units.
The [published-count reconciliation](_support/relay/count-reconciliation.json) checks the original narrative table against its output.

The SEC and relay wiki counts differ intentionally.
SEC restricts June 18 and literal `county.json` in added ranges.
Relay counts URL-like tokens over the export and permits bounded percent-decoding.
Neither is a verified count of messages read by other agents.

## 6. Public relay projects and historical endpoint records

**Type:** pinned source code, repository metadata, documentation, and bounded CDX queries.
**Useful for:** pre-existing project history, intended endpoint behavior, and historical service observations.
**Limit:** current code or a no-key example does not prove June deployment configuration or target success.

Read [historical metadata](_support/relay/historical-evidence.json) and [project manifests](_support/relay/project-source-manifest.json).
Read [source excerpts](_support/relay/source-excerpts.md) for JQP, Hexlet, cors.lol, and Lemino evidence.
The [source-evidence manifest](_support/relay/source-evidence-manifest.json) maps source IDs to raw-body hashes and excerpt headings.
The parent independently confirmed all 22 referenced raw-source hashes.
See [parent hash verification](_support/parent-relay-hash-verification.json).

Service capabilities and comments support intended functions only.
They do not prove which function any historical actor executed.

## 7. Published investigations and novelty checks

**Type:** Transluce reports, Manifold reporting, Asymmetric findings, DeGraff's investigation, and related publications.
**Useful for:** prior-publication scope and exact wording.
**Limit:** publications can share original datasets or copy claims.

Read [novelty excerpts](_support/novelty/source-excerpts.md).
The [publication metadata](_support/novelty/publication-metadata.jsonl) preserves publication/discovery distinctions.
The [search ledger](_support/novelty/search-ledger.jsonl) records the bounded search universe.

“No prior publication found in these searches” is permitted.
“Nobody published this” is not established.
A source's current presence in a repository does not establish its first public publication date.

## 8. Public-feed controls and access documentation

**Type:** feed-query receipts and public API/search documentation.
**Useful for:** testing whether the same detector rediscovers known historical activity.
**Limit:** public coverage, private reports, retention, indexing, authorization, and query timeouts differ.

The [feed ledger](_support/novelty/feed-tests.jsonl) records exact paired queries and responses.
The [query receipts](_support/novelty/query-receipts.md) provide a readable view.
Failed requests and unavailable controls MUST NOT become zero-count observations.
GreyNoise's authorization failure is retained as such.

## 9. WET-BOEW parameter semantics

**Type:** official toolkit documentation.
**Useful for:** interpreting `wbdisable=true` as Basic HTML mode.
**Limit:** the documented feature does not establish request intent or actor identity.

Read the [preserved excerpt](_support/wet-boew-excerpt.md).
The documentation displays a July 11, 2023 modification date.
The parent retrieved it during this review.

## Preservation and coverage limits

The collection retains redacted metadata, selected excerpts, scripts, queries, and response hashes.
It does not retain every publication's complete body.
Some child raw downloads remain in scratch or ignored `data/raw/`.
Their loss would require renewed retrieval for full-body reanalysis.
The shareable support files preserve the narrow evidence used here.

Exact UTC retrieval times are retained where tool receipts supplied them.
Some publication ledger entries preserve only an access date.
Those entries MUST NOT be presented as more precise than the retained receipt.

The final [verification manifest](_support/verification.json) hashes the reviewed document and support set.
Mechanical verification authenticates files and mappings, not causal conclusions.
