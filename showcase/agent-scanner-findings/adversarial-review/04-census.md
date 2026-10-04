# Item 4 — Census: May 24 reports and June 17 relay claim

**Disposition: C — split the claim.**
Two May 24 browser reports support an earlier observed key-bearing request family.[3][4]
They do not establish the start of an agent operation.
The June 17 records do not establish a three-hop chain or successful relay retrieval.[11][12][13]

## Strongest surviving claims

- On May 24, two urlquery browser runs sent the same malformed ACS5 URL to `api.census.gov`.[3][4]
- Both URLs contain the same 40-character key indicator as the brief. This comparison occurred in memory.[3][4]
- Both browser runs reached `api.census.gov` and received HTTP 302, then the `Missing Key` page.[3][4]
- On June 17, Wayback captured three separate relay URLs for one public Census static file.[8][9][10]
- Separate Wayback captures contain the static file. No record links them to the relay requests.[14][15]

The May 24 observation changes the **observed chronology**, not the proven operation start.[1][3][4]
The June 17 evidence changes the proposed **mechanism and outcome** from retrieval to failed relay attempts.[11][12][13]
Confidence is high for the records and failures. Confidence is low for agent attribution.

## Prior claims under review

The [original brief](../discord-brief-2026-10-03.md) calls May 24 the start of exposed-key reuse.
It also calls June 17 a successful three-relay retrieval.
The later [claim matrix](../claim-matrix-2026-10-03.md) repeats both claims in C3.
It marks C3 independently reproduced and assigns high confidence.
The primary records support the earlier May 24 trace, not an operation start.[3][4]
They contradict the claimed relay success and hop sequence.[11][12][13]
Treat the matrix as a claim source, not independent primary corroboration.

## May 24: request, target, and content

The safe URL shape is `https://api.census.gov/data/2022/acs/acs5?get=NAME%2CB01002_001E%2CB19326_001E%26for=state:*%26key=[REDACTED]`.[3][4]
Both reports use that exact submitted URL. They are separate browser reports, not evidence of separate agents.[3][4]
The literal `%26` occurs twice. Standard query parsing leaves only the `get` parameter.
The `for` and `key` strings remain inside its decoded value.[3][4]
The server therefore did not receive a separate `key` query parameter.[3][4]
The recorded HTTP transactions show `GET` and HTTP 302 to `/data/missing_key.html`.[3][4]
That page returns HTTP 200 and has the title `Missing Key`.[3][4]
An HTTP 200 error page is **not** a successful ACS data response.[3][4]
Do not test the key or infer whether an unmalformed request would work.

The released `report-sources.csv` assigns five reports to `US Census API`.
The May 12 report visits an unrelated website. Its browser loads a Census subresource without this indicator.[5]
The two June 3 reports visit another website. Their Census subrequests use different keys or no key.[6][7]
This classification is not an exhaustive history of Census requests.
The May 24 reports are the earliest **matching key-bearing reports in this bounded check**.[3][4][5]

## June 17: no three-hop chain

The three archived URLs point **directly** to the same `www2.census.gov` B16001 `.dat` path.[8][9][10]
None embeds another relay. Jina uses `http` for the target; the other two use `https`.[8][9][10]
Thus, the forwarded URLs do not match exactly.[8][9][10]
The capture order is Jina, AllOrigins, then CorsProxy. This order also contradicts the claimed hop order.[8][9][10]

| Archive time UTC | Wrapper | Outer response | Returned material | Raw ref |
| --- | --- | --- | --- | --- |
| 02:59:07 | Jina | 200 | Source metadata; empty `Markdown Content:` | [8][11] |
| 03:02:12 | AllOrigins | 500 | Nginx internal-error page | [10][12] |
| 03:03:01 | CorsProxy | 403 | Free-use restriction error | [9][13] |

Jina's `Published Time` is an August 2023 file timestamp. It is not June 2026 source time.[11]
A relay HTTP 200 does not show that file data returned.[11]
The three URLs could reflect retries by one actor. They could also reflect independent archive submissions.
Neither explanation has a shared initiator, request ID, or observed handoff.

Wayback separately captured the target file at 02:39:07 and 05:26:13 UTC.[14]
Both direct replays return 993,783 bytes with the same SHA-256 digest.[14][15]
The file begins with a `GEO_ID|B16001` header.[15]
These records establish retrieval **by the archive** of a public file.[14][15]
They do not establish receipt of a relay request or consumption by an agent.[11][12][13]
This static `www2.census.gov` file is not the May 24 `api.census.gov` ACS5 request.
It carries no exposed key in these archived URLs.[8][9][10]

## Strict chronology and time types

| Observed UTC time | Unit | Layer | Primary ref |
| --- | --- | --- | --- |
| May 24 07:08:39.335 | Browser HTTP GET | Census API receipt; 302 | [3] |
| May 24 07:08:41.987 | Browser HTTP GET | Census API receipt; 302 | [4] |
| June 17 02:39:07 | Archive capture | Direct file replay returns data | [14][15] |
| June 17 02:59:07 | Archive capture | Jina wrapper returns metadata | [8][11] |
| June 17 03:02:12 | Archive capture | AllOrigins returns error | [10][12] |
| June 17 03:03:01 | Archive capture | CorsProxy returns error | [9][13] |
| June 17 05:26:13 | Archive capture | Second direct file replay returns the same data | [14] |

Urlquery lists the two May 24 reports at 07:09:00 and 07:09:03 UTC.[3][4]
These report times differ from the earlier HTTP transaction times.
Wayback CDX times are **archive times**.[8][9][10]
The originator's source time is unknown.
This investigation found these records on 2026-10-04 UTC.
Transluce published its Census statement on 2026-09-30.[1]
The brief's date is 2026-10-03. Do not substitute either publication date for event time.

## Exact comparison with Transluce

Transluce says: “Between June 16 and 22, publicly posted URLs indicate attempts to reuse exposed API keys to access census.gov data.”[1]
It adds: “We do not share underlying URLs in this case to avoid republishing sensitive materials, and found no response showing that these attempts were successful or ever reached census.gov.”[1]
Its statement concerns the specified **June 16–22 exposed-key request family**.
May 24 is outside that interval.[1][3][4]
The direct May 24 receipt does not contradict its scoped claim.[1][3][4]
The June 17 file is a different, key-free `www2.census.gov` request family.[8][9][10]
Its direct archive copies cannot establish success for Transluce's exposed-key attempts.
The brief's shorter quotation omits the original scope and its separate success condition.[1]

## Claim ladder, alternatives, and limits

The May 24 records reach level 3: the browser recorded Census HTTP responses.[3][4]
They show an error-page effect, but no requested data.[3][4]
No actor-family link reaches level 5.
The three relay captures establish level 1 archive artifacts and relay responses.[8][9][10]
They do not establish chained destination receipt or successful relay content retrieval.
The direct file archives establish a separate archive retrieval, not a relay-chain effect.[14][15]

Reject “May 24 was the operation start,” “three-relay retrieval,” and “Transluce was contradicted.”
A benign URL submission or unrelated tool could explain the two May 24 reports.
Separate retries or ordinary archive submissions could explain the June 17 cluster.
Server-side logs, initiator records, or a shared request ID would discriminate these explanations.
No such record was found in this bounded check.

No earlier account of these exact records appeared in the searched sources.
This is a **bounded search result**, not proof that nobody published them.
See [`search-coverage.md`](_support/census-aihw/search-coverage.md) for queries and blocked routes.
See [`census-may24-redacted.json`](_support/census-aihw/census-may24-redacted.json) and [`census-june17-redacted.json`](_support/census-aihw/census-june17-redacted.json) for raw refs.
The JSON files omit all credential values. Public urlquery report pages may still display them.

## Sources

[1] https://transluce.org/us-canada-gov — Transluce Census
[3] https://urlquery.net/report/87465efc-fc5e-484a-8089-b99f6981f575 — May24 report A
[4] https://urlquery.net/report/7d967df7-fcf5-4df1-927b-2642039a7b84 — May24 report B
[5] https://urlquery.net/report/03b8111f-1e02-4ac2-9772-e9ef2bcf4f1a — May12 false-positive
[6] https://urlquery.net/report/29a660a2-13c9-4744-83d0-3ea58c40bb7f — June03 report A
[7] https://urlquery.net/report/7d203adc-9eff-401b-9a31-35a9c7155d30 — June03 report B
[8] https://web.archive.org/cdx/search/cdx?url=r.jina.ai%2Fhttp%2A&from=2026061702&to=2026061703&filter=original%3A.%2Acensus.%2A&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cstatuscode%2Cmimetype%2Cdigest%2Clength — Wayback Jina Census CDX
[9] https://web.archive.org/cdx/search/cdx?url=corsproxy.io%2F%2A&from=2026061702&to=2026061703&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cstatuscode%2Cmimetype%2Cdigest%2Clength — Wayback CorsProxy CDX
[10] https://web.archive.org/cdx/search/cdx?url=api.allorigins.win%2F%2A&from=2026061702&to=2026061703&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cstatuscode%2Cmimetype%2Cdigest%2Clength — Wayback AllOrigins CDX
[11] https://web.archive.org/web/20260617025907id_/https://r.jina.ai/http://www2.census.gov/programs-surveys/acs/summary_file/2022/table-based-SF/data/1YRData/acsdt1y2022-b16001.dat — Wayback Jina replay
[12] https://web.archive.org/web/20260617030212id_/https://api.allorigins.win/raw?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback AllOrigins replay
[13] https://web.archive.org/web/20260617030301id_/https://corsproxy.io/?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback CorsProxy replay
[14] https://web.archive.org/cdx/search/cdx?url=www2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat&from=20260617&to=20260617&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cstatuscode%2Cmimetype%2Cdigest%2Clength — Wayback Census static-file CDX
[15] https://web.archive.org/web/20260617023907id_/https://www2.census.gov/programs-surveys/acs/summary_file/2022/table-based-SF/data/1YRData/acsdt1y2022-b16001.dat — Wayback Census direct replay
