# 09 — Corrected claim ledger and matrix crosswalk

The six original items split into 15 independently assessed subclaims.
The [machine-readable ledger](_support/corrected-claims.json) carries every required field.
It includes original wording, surviving wording, level, evidence, confidence, alternatives, missing evidence, novelty, and changed dimensions.

Disposition key: A unchanged; B narrower; C split; D unproved; E contradicted/artifact; F unverifiable.
Level refers to the specified observation layer, not authenticated agent involvement.

## Overall disposition of each original item

| Item | Disposition | Boundary |
| --- | --- | --- |
| 1 — SEC captures | C — split | Burst survives; counts change; mechanism and attribution remain unproved. |
| 2 — Common operation | D — unproved | Treat the clusters as related-looking but independent. |
| 3 — Relay layer | C — split | Reference counts survive under explicit units; stronger infrastructure and novelty claims fail. |
| 4 — Census | C — split | Earlier failed requests survive; successful triple-relay retrieval does not. |
| 5 — AIHW | C — split | Malformed capture survives; workbook retrieval and pharmaceutical linkage do not. |
| 6 — Dormancy | B — narrower | Retain only the bounded public-index comparison, not cessation. |

## Original brief: corrected subclaims

| ID | Disposition | Level | Strongest surviving statement | Evidence route |
| --- | --- | ---: | --- | --- |
| I1-count | C | 1 | Current query: 63 index entries; 62 URL keys; 60 entries share the main digest | [1](01-sec-wayback.md) |
| I1-nonce | C | 1 | 41 x-decimal entries have variable digit lengths; seven have 17 digits | [1](01-sec-wayback.md) |
| I1-order | C | 1 | Wiki predates the first bare-decimal capture, but follows earlier archive entries | [1](01-sec-wayback.md) |
| I2-operation | D | 1 | Retain related-looking independent clusters; SEC shares a target | [2](02-operation-linkage.md) |
| I2-reports | C | 2 | 13 report IDs correspond to seven submitted URLs within the stated interval | [2](02-operation-linkage.md) |
| I3-count | C | 1 | Defined cumulative corpus: 17086/46278 outer-host occurrences; hunk counts differ | [3](03-relay-layer.md) |
| I3-hosts | E | 0 | 480 labels generic CORS proxies; source inventory already names Lemino | [3](03-relay-layer.md) |
| I3-infrastructure | B | 1 | Several referenced services predate the burst; full infrastructure scope is unknown | [3](03-relay-layer.md) |
| I4-earlier | C | 3 | Two matching May 24 browser requests reached Census and ended at Missing Key | [4](04-census.md) |
| I4-chain | E | 1 | Three separate archive wrappers return empty content or errors; no chained hops | [4](04-census.md) |
| I4-direct | C | 4 | Two independent target captures contain a different, key-free static file | [4](04-census.md) |
| I5-capture | C | 2 | One capture preserves the doubled scheme; returned text is a security check | [5](05-aihw.md) |
| I5-incident | D | 1 | The diagnosis resource differs; earlier AIHW activity was already published elsewhere | [5](05-aihw.md) |
| I6-zero | B | 0 | Only a scoped urlquery comparison has a useful county-string June control | [6](06-dormancy-and-novelty.md) |
| I6-ended | D | 0 | Public-feed silence cannot establish cessation | [6](06-dormancy-and-novelty.md) |

## Later matrix: all entries accounted for

The matrix is more explicit but is not primary evidence.
Its new leads do not silently expand verified scope.

| Matrix ID | Review status | Narrow finding or missing prerequisite |
| --- | --- | --- |
| C1 | Local count reproduced | 14,941 capture rows contain literal `zz=oai`. This is corroboration, not actor authentication. |
| C2 | Split | June 18 diagnosis-cube wrapper returned a block. It is not the later pharmaceutical resource. |
| C3 | Split and corrected | May 24 receipt survives; triple-relay success does not. |
| C4 | Split and corrected | Current SEC query returns 63 raw entries, not 65. Agent-driven capture is unproved. |
| C5 | Not re-examined | Matrix itself excludes renewed LAC incident verification. |
| C6 | Corrected | Relay references survive. Denominator and host/category assignments need correction. |
| C7 | Narrowed | Wiki/Wayback peak overlap survives; “same operation” does not. |
| C8 | Unverified extension | No NPWS trace set or exact host was supplied. “Our first writeup” needs its own novelty review. |
| C9 | Local scope differs | Supplied ZIP: 561,229 capture rows; 42,483 `zzbulk` rows; 27,865 `prepnonce` rows. |
| C10 | Semantic correction supported | WET-BOEW documents `wbdisable=true` as Basic HTML mode.[18] Nine LAC rows contain the term. |
| C11 | Narrowed | No comprehensive three-feed zero or operational dormancy is established. Arquivo degradation remains separately unverified. |
| C12 | Demotion appropriate but incomplete | Toolkit resemblance is a hypothesis; C7 and prose still assert common operation. |
| C13 | Unverified extension | Exact SwarmMemo post, thread history, and provenance were not supplied. No actor linkage established. |
| C14 | Unverified extension | Named skill/version and seven-file inventory were not supplied. Capability instructions would not prove historical execution. |
| C15 | Not re-investigated | Prior-publication attribution remains a matrix statement; no new incident claim is admitted. |

C1, C9, and the local part of C10 use [matrix-local-counts.json](_support/matrix-local-counts.json).
The rule is case-sensitive literal matching in `target_url`, with no decoding.
C9's 589,972 denominator does not match this ZIP's capture-row population.
Its 42,677 and 27,860 figures do not match this stated count rule.
This does not prove the absent briefdump used the same inputs or filters.

The WET documentation identifies a normal page feature.[18]
It does not establish any requester's intent.
The displayed modification date is July 11, 2023.[18]

## Required status boundaries

“Unverified extension” is not a negative finding.
The missing briefdump may supply the evidence needed for those additional entries.
Do not convert a missing source into a disproved event.

No item in the original six survives with every headline implication unchanged.
This is not a finding that all underlying traces are false.
It separates valid archival observations from failed mechanism, attribution, and novelty claims.

## Sources

[18] https://wet-boew.github.io/wet-boew/docs/ref/wb-disable/wb-disable-en.html — WET-BOEW Basic HTML documentation
