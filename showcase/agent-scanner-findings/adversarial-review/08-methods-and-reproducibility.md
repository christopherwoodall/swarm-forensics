# 08 — Archival method, units, contamination, and reproduction

## Scope

Review the six original headline claims against primary records.
Use the later claim matrix as another claim source.
Do not treat either document, or earlier conversations, as corroboration.

Public index queries, archive replays, and published-source retrieval were read-only.
No archive save was initiated.
No credential was validated or used to access a service.
No human/operator identity investigation occurred.

## Four clocks

| Field | Meaning | Rule |
| --- | --- | --- |
| Source time | Time recorded for the underlying request or edit | Preserve the source's precision and time grade |
| Archive time | Time in the archive's capture record | MUST NOT substitute for an unknown client request time |
| Discovery time | This review's retrieval time | Recorded in receipts; mostly 2026-10-04 UTC |
| Publication time | Date a source published its account | Does not establish a June action |

The brief and matrix are dated 2026-10-03.
Retrieval crossed the UTC date boundary while local time remained October 3.
Unknown times remain null in structured records.
Source-report clocks and HTTP-entry clocks are not interchangeable.

## Evidence ladder

| Level | Required evidence | Important limit |
| --- | --- | --- |
| 0 | Reproducible artifact | Existence only |
| 1 | Action-shaped trace | URL syntax does not prove execution |
| 2 | Issued action attempt | Originator identity can remain unknown |
| 3 | Destination receipt | Relay receipt is not target receipt |
| 4 | Specific returned content or effect | Name the effect; an error page is not the requested dataset |
| 5 | Defensible actor-family association | Needs evidence beyond fluent text or nonce syntax |
| 6 | Common-operation linkage | Needs evidence beyond target, date, or relay overlap |

Apply levels to a specified layer and effect.
They are not a score where HTTP 200 automatically permits actor attribution.
A successful archive replay does not establish a successful original agent task.

## Units table

| Unit | Count only when | MUST NOT become |
| --- | --- | --- |
| Archive index entry | One row in a stated CDX response | One agent save or origin request |
| Unique URL string | Exact string equality under a stated parser | Unique activity episode |
| URL key | Archive-normalized indexing key | Exact original URL |
| Browser report | Stable urlquery report ID | Agent, operation, or single HTTP request |
| HTTP entry | Report ID plus entry index | Successful target fetch |
| Relay hop | Forwarding relation is demonstrated | Each nearby relay observation |
| Target request | Intended target receipt is evidenced | Outer relay HTTP status |
| Successful requested response | Body matches the requested resource | Any HTTP 200 page |
| Wiki occurrence | Literal occurrence under a specified extraction method | Request or readership |
| Wiki revision | Stable revision record | New message for every inherited line |
| Name or label | Preserved visible string | Authenticated actor |
| Session | Explicit session boundary | Every package, URL, or report |
| Incident | Defined affected-service episode | Each article discussing it |
| Operation | Demonstrated common control/activity boundary | A temporal cluster |

## Acquisition and response-body checks

CDX exposes index metadata not present in the bundled urlquery catalog.[1]
Archive replays can reveal content hidden by a simple status-code table.[4][5][6]
They do not automatically expose capture submitters or target-server logs.

The parent re-fetched all three Census wrappers and the AIHW wrapper.
All four decoded response hashes matched the independent child measurements.
See [parent-replay-verification.json](_support/parent-replay-verification.json).
The Census results were empty Jina content, AllOrigins error, and CorsProxy restriction.[4][5][6]
AIHW returned a Jina-reported target block.[8]

The supplied US/Canada ZIP includes 51 response-file or response-excerpt members.
This contradicts our earlier blanket assertion that all packages lack response bodies.
Presence alone does not establish an agent received those bodies.
The SEC CSV's body-presence field describes its source JSON, not necessarily bytes bundled locally.
See [parent-measurements.json](_support/parent-measurements.json) for the member inventory.

## Duplicates and normalization

CDX collapse removes one SEC revisit and changes which bare-URL response remains visible.[1]
Therefore count raw rows and collapsed rows separately.
Record digest equality as index-digest equality unless replay bytes were checked.

For wiki text, include new content from both `insert` and `replace` hunks.
Keep cumulative-body occurrences as a separate sensitivity count.
Reference counts from cumulative bodies inflate repeated surviving text.
These counts are not independent replications.

URL normalization MUST preserve an exact-string channel.
Treat case, slash, percent-encoding, or parameter-normalized matches as separate channels.
Never repair a malformed source token before validating its original form.
Do not expand URL variants recursively without a finite bound.

## Contamination and circularity

| Evidence path | Potential dependence | Consequence |
| --- | --- | --- |
| Wiki export → selected-record corpus → link index | Same originating text may appear in three formats | Not three independent witnesses |
| Transluce ZIP → local pipeline → viewer → research note | Derived counts reuse one export | Prior notes only locate records |
| Report → search terms → scanner hits | Selection is conditioned on the hypothesis | Cannot estimate population prevalence |
| Browser report → archive replay | Archiving can preserve scanner-generated traffic | Initiator and client context remain unknown |
| June timestamp → September report | June predates that publication | Does not exclude earlier research or later indexing |
| Current registry metadata → June narrative | Metadata lacks publication time | MUST NOT place package creation on a June timeline |

A `ResearchUser`-style name is not proof of investigator identity.
A `OpenAI`-style name is not authentication of an OpenAI runtime.
Different IP blocks do not authenticate separate actors.
A null comparison without uncertainty or exchangeability checks does not establish “at chance.”

## Previous pipeline issues identified, not repaired here

The review does not use the active edge table as primary evidence.
Source inspection found three reasons to quarantine earlier headline counts:

- `wiki_exchange.py:159` uses `_lag(...)` as a Boolean window test.
- `_lag` returns nonempty strings and never applies its `default` argument at lines 239–252.
- Therefore the claimed six-hour pairing bound is not enforced.

Further, `bridges.py:77–86` joins all link records without checking wiki-origin membership.
A registry record can enter the supposed wiki side of a gem-to-wiki overlap.
The current pairing code also uses process-randomized `hash()` values for edge IDs.
These findings require a separate code repair and full re-extraction.
No existing graphs or raw archives were overwritten during this review.

Acknowledgment vocabulary alone is not verified uptake.
“Confirmed by system” can match a generic acknowledgment expression without acknowledging another participant.
Repeated numeric tokens can be task identifiers or common answers rather than transmitted results.

## Statistical checks and limits

The SEC chapter measures hourly counts, adjacent gaps, digest proportions, and coincidence windows.
The relay chapter supplies denominator and deduplication sensitivity.
The dormancy chapter requires same-query historical controls.

None supplies a representative ordinary-human population for actor classification.
No causal significance test is claimed for the wiki/Wayback overlap.
No global cessation test is possible from the inspected public-feed coverage.

## Reproduction

Run from the repository root:

```sh
make review-measure
make review-verify
make --assume-old=setup test lint RUN='uv run --frozen --offline --no-sync'
```

`review-measure` re-reads the pinned local ZIPs and reconciles retained CDX metadata.
It does not issue network requests.
`review-verify` checks document coverage, local links, citations, parseability, and known-key redaction.
Its hash inventory binds verification to the exact saved files.
Neither command proves a source's scientific interpretation.

For external reproduction, use the exact queries and retrieval times in each chapter's support directory.
Failed requests remain recorded as failures, never empty successful searches.
Raw parent replay bytes are under ignored `data/raw/adversarial-review/parent-replays/`.
Share the redacted support files, not unreviewed raw bodies.

The matrix names `briefdump-2026-10-03.zip`.
That file was not found in this repository during discovery.
Original scanner query receipts and that dump remain missing inputs.

## Sources

[1] https://web.archive.org/cdx/search/cdx?url=sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260618&to=20260618&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cdigest%2Cstatuscode%2Cmimetype%2Clength%2Cfilename%2Coffset
[4] https://web.archive.org/web/20260617025907id_/https://r.jina.ai/http://www2.census.gov/programs-surveys/acs/summary_file/2022/table-based-SF/data/1YRData/acsdt1y2022-b16001.dat — Wayback Jina replay
[5] https://web.archive.org/web/20260617030212id_/https://api.allorigins.win/raw?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback AllOrigins replay
[6] https://web.archive.org/web/20260617030301id_/https://corsproxy.io/?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback CorsProxy replay
[8] https://web.archive.org/web/20260618063135id_/https://r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/Principal-Diagnosis-cube_2014-15.xlsx.aspx — Wayback AIHW replay
