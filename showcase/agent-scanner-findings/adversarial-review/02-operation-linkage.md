# 02 — Operation linkage and competing explanations

## Decision

**Treat the four clusters as related-looking but independent.**
A provisional research group is useful.
A merged operation is not established.

The brief groups Census, AIHW, SEC Wayback, and SEC urlquery activity.
The matrix demotes C12 to toolkit-level linkage.
However, C7 and the matrix's prose still say “same operation, two venues.”
The demotion does not resolve those remaining claims.

## Four independently defined clusters

| Cluster | Record boundary | Narrow finding | Evidence |
| --- | --- | --- | --- |
| CEN17 | Three June 17 relay captures | Separate wrappers name one Census static file; none returns its data | [4][5][6] |
| AIHW18 | One June 18 Jina capture | Malformed wrapper returns a security-check page | [8] |
| SEC-WB18 | June 18 SEC-path CDX prefix query | 63 entries; 62 URL keys; unknown capture initiator | [1] |
| SEC-UQ18 | Released SEC HTTP export | 568 entries contain literal `county.json`; 546 report IDs | Local measurement M1 |

CEN17 is not the May 24 exposed-key API family.[2][3][4]
AIHW18 concerns hospital diagnosis, not the pharmaceutical task in Transluce's case.[8][10]
Neither common agency names nor common months erase those boundaries.

M1 is `_support/parent-measurements.json`.
Its source ZIP hashes and CSV row references permit local reproduction.
The original reports and HTTP entries remain different units.

## Comparison matrix

“Unknown” means unavailable in the inspected records, not absent historically.

| Feature | CEN17 | AIHW18 | SEC-WB18 | SEC-UQ18 | Linkage reading |
| --- | --- | --- | --- | --- | --- |
| Exact time | 02:59:07, 03:02:12, 03:03:01, June 17 | 06:31:35, June 18 | 02:23:00–20:21:25, June 18 | 04:23:09.763–23:27:19.644, June 18 | Temporal overlap or proximity only |
| Clock type | Archive capture | Archive capture | Archive capture | Browser HTTP-entry time | Different clocks MUST remain separate |
| Target | Public B16001 static file | Principal-diagnosis workbook | SEC county file | County URLs and wrappers | SEC pair shares a target; others differ |
| URL grammar | Three independent wrappers | Doubled scheme | Path-prefix variants | Direct and relay URLs | Mostly public-service conventions |
| Nonce grammar | Not an admitted linking feature | Not an admitted linking feature | Decimal and other queries | Several query forms | No authenticated shared generator |
| Relay choice | Jina, AllOrigins, CorsProxy | Jina | Unknown capture path | Several public relays | Shared Jina is weak family resemblance |
| User-agent | Unknown | Unknown | Unknown | Export contains browser user-agent | No cross-cluster exact match demonstrated |
| Request method | Historical method unavailable | Historical method unavailable | Unknown | Export contains method | Review GETs MUST NOT become historical methods |
| Path quirks | HTTP versus HTTPS target | `http://https://` | Query and slash variants | Includes malformed `/file/countyjson` | Different quirks do not identify one program |
| Credential reuse | Static file has no key | None established | None established | None establishes this linkage | May 24 key belongs to another request family |
| Archive/platform | Wayback | Wayback | Wayback | urlquery export | Archive reuse is an observation-source link |
| Source IP/ASN | Unknown | Unknown | Unknown | Remote peer IP available | Remote peer is destination-side, not submitter identity |
| Headers | Historical request headers unavailable | Same | Same | No shared originator header established | No discriminator |
| Payload structure | Target URL only | Target URL and relay text | Index metadata | Request metadata | No shared task payload established |
| Task vocabulary | Language table | Hospital diagnosis | County data | SEC task family | Different workloads remain separate |
| Wiki reference | No explicit relay-to-wiki handoff established | No explicit handoff established | Concurrent county references | Export cites a county wiki revision | Reference is not causal consumption |
| Shared filename | B16001 `.dat` | Principal Diagnosis `.xlsx.aspx` | `county.json` | `county.json` | Moderate workload linkage for SEC pair only |
| Shared identifier | No unique identifier across all four | None | None linking initiator | Report IDs only local to reports | No strong unique operation link |
| Explicit handoff | Not found | Not found | Not found | Not found across clusters | Common operation unsupported |

The Census and AIHW fields derive from captured responses and CDX records.[4][5][6]
AIHW's response names its target and reports a block.[8]
SEC archive fields derive from CDX.[1]
SEC HTTP fields derive from M1, not the CDX index.

## Unit correction in the late SEC window

The brief calls 22:34–23:27 UTC “7 urlquery reports.”
The released report CSV has 13 distinct report IDs in that interval.
Those rows contain seven distinct submitted URL strings.
They declare 258 HTTP entries in total.
This reproduces seven **submitted URLs**, not seven reports.
The retained row references are in M1 under `sec_http.late_reports`.

The claimed 252 block-page hits remains unverified.
A status histogram is not a block-page count.
No response-body fingerprint was supplied for that count.
HTTP 200 MUST NOT be equated with useful county JSON.

## Hypothesis comparison

| Hypothesis | Evidence compatible with it | Strongest difficulty | Smallest useful discriminator |
| --- | --- | --- | --- |
| A. One operation | Nearby dates; public-relay reuse | No shared initiator or handoff; different task families | Shared authenticated run ID across target-specific traces |
| B. Independent agents under one harness | Similar wrappers and output conventions | No harness configuration tied to all four | Versioned harness trace linked to each request |
| C. Unrelated operations using public tools | Generic relay services; distinct resources | SEC temporal clustering deserves explanation | Strong identifier overlap exceeding a service-usage baseline |
| D. Archive/search selection | Queries selected targets and dates from known reports | Cannot explain all underlying requests by itself | Predeclared broad search and ordinary-day controls |
| E. Human or system automation | Nonces and retries are ordinary software patterns | Agent-associated wiki material exists nearby | Capture-submitter provenance, not merely URL appearance |
| F. Investigator contamination | Reused exports and later report-based searches | June timestamps precede September reports | Submission logs, export lineage, and original ingestion records |

These hypotheses remain alternatives, not measured posterior probabilities.
No validated likelihood model supports numeric operation probabilities here.

## Evidence graph

Use [operation-graph.json](_support/operation-graph.json).
Nodes distinguish clusters, targets, relays, identifiers, grammars, and publications.
Edges name only the observed relation or explicitly labeled hypothesis.
Each edge records analyst, source, observation time, basis, and confidence.

The graph has no `same_operation` edge.
Temporal proximity and shared targets MUST NOT imply one through visual layout.
A shared public URL identifies an object, not the actor that used it.

## Strongest alternative

Independent tasks reused accessible public retrieval tools during a busy evaluation period.
This explains timing, wrappers, and common file references without any cross-target handoff.
A shared evaluation schedule is also a hypothesis, not established runtime evidence.

## Consequence for previous findings

My earlier “same operation, hour for hour” endorsement is withdrawn.
Temporal overlap remains; operation identity does not.
The earlier “three-bed” chronology cannot date gem publication from records labeled `current`.
The review preserves those earlier texts as prior hypotheses.
It does not silently rewrite them or the active visualization data.

## Independent-reader test

A skeptical reader could identify a busy SEC retrieval topic across observation surfaces.
They could identify Census relay failures and a separate AIHW blocked request.
They would need our narrative to merge all four clusters.
That merger MUST remain a hypothesis.

## Sources

[1] https://web.archive.org/cdx/search/cdx?url=sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260618&to=20260618&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cdigest%2Cstatuscode%2Cmimetype%2Clength%2Cfilename%2Coffset
[2] https://urlquery.net/report/87465efc-fc5e-484a-8089-b99f6981f575 — May24 report A
[3] https://urlquery.net/report/7d967df7-fcf5-4df1-927b-2642039a7b84 — May24 report B
[4] https://web.archive.org/web/20260617025907id_/https://r.jina.ai/http://www2.census.gov/programs-surveys/acs/summary_file/2022/table-based-SF/data/1YRData/acsdt1y2022-b16001.dat — Wayback Jina replay
[5] https://web.archive.org/web/20260617030212id_/https://api.allorigins.win/raw?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback AllOrigins replay
[6] https://web.archive.org/web/20260617030301id_/https://corsproxy.io/?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback CorsProxy replay
[8] https://web.archive.org/web/20260618063135id_/https://r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/Principal-Diagnosis-cube_2014-15.xlsx.aspx — Wayback AIHW replay
[10] https://transluce.org/agent-activity — Transluce AIHW
