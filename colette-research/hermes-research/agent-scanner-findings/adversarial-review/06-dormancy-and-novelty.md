# 06 — Dormancy and novelty audit

## Result

**Reject item 6 as written.** The public searches do not establish that an operation stopped.[17][29][32]

The urlquery public search recovered June county-file reports with an unchanged query.[17][18]
It showed no matching reports in the recent date bucket.[17][18]
The same interface showed recent AIHW and Jina reports.[20][23]
Those broad matches do not establish renewed activity by the June actor family.[20][23]
Other marker queries failed their June controls.
The urlscan June control failed even for a broad unrelated domain.[29]
GreyNoise query access returned HTTP 401.[32]

Use this narrower statement: “No county.json reports matched the stated urlquery query in the queried recent public index.”[18]
Do not write “the operation stopped,” “the machinery is dormant,” or “zero fingerprints in any feed.”[29][32]

The novelty review found prior publication of much of the relay layer and the earlier AIHW window.[9][10][12]
The bounded [search ledger](_support/novelty/search-ledger.jsonl) has no confirmed prior mention of the exact AIHW Jina key.
That search result is not proof of first publication.

## Scope and clocks

- **Source window:** June 17–23, 2026, with narrower June 18 controls where shown.[17][24]
- **Recent window:** September 4–October 4, 2026, inclusive calendar dates in feed queries.[18][23]
- **Actual 30-day cutoff:** Approximately October 4, 01:22 UTC minus 30 days.
- **Window error:** The calendar filter includes early September 4 before the exact cutoff.[18]
- **Discovery time:** This pass retrieved results on October 4, 2026, around 01:11–01:24 UTC.
- **Archive time:** The AIHW CDX key is `20260618063135`; that is a capture timestamp.[33]
- **Publication time:** Transluce reported on September 23 and September 30, not in June.[13][14]
- **Prior publication:** Manifold states September 25; Asymmetric states September 28.[9][12]
- **Earlier archive:** Wayback lists a September 24 capture of Transluce’s September 23 report.[35]

The [brief](../discord-brief-2026-10-03.md) gives no original search strings, feed responses, or search time.
These are new, explicit tests.
They do not reproduce an undisclosed original search.

## Positive-control audit

Each pair uses the **same query field and term** on the **same platform**.[17][18]
Only the date bucket changes.[1][17][18]
“Hits” are interface search matches, not HTTP requests, agents, or successful target fetches.[7]
The urlquery interface can match submitted URLs and HTTP activity inside reports.[7]

| urlquery field and literal | June bucket, UTC | June UI hits | Recent UI hits | Reading |
| --- | --- | ---: | ---: | --- |
| `http.url.addr:*county.json*` | June 17–19 | 548 [17] | 0 [18] | Usable target-string control. |
| `url.addr:*county.json*` | June 17–23 | 436 | 0 | Submitted-URL control; see feed ledger. |
| `http.url.addr:*sec.gov/files/county.json*` | June 17–19 | 444 | 0 | Narrower target-string control; see feed ledger. |
| `http.url.addr:*aihw.gov.au*` | June 17–23 | 4,376 [19] | 7 [20] | Target remains visible; actor linkage unknown. |
| `http.url.addr:*jqp.vercel.app*` | June 17–23 | 3 [21] | 0 [22] | Thin June control; no global relay census. |
| `http.url.addr:*r.jina.ai*` | June 17–23 | 76 [24] | 4 [23] | Relay remains visible; submissions differ. |
| `http.url.addr:*api.cors.lol*` | June 17–19 | 3 [25] | 0 [26] | Thin June control. |
| `http.url.addr:*allorigins.hexlet.app*` | June 18–19 | 94 [27] | 0 [28] | Narrow retry succeeded; broad June query stalled. |
| `http.url.addr:*zz=oai*` | June 17–19 | 0 | 0 | Failed positive control. |
| `http.url.addr:*zzbulk*` | June 17–19 | 0 | 0 | Failed positive control. |
| `http.url.addr:*prepnonce*` | June 17–19 | 0 | 0 | Failed positive control. |
| `http.url.addr:*openai_research*` | June 17–19 | 0 | 0 | Failed positive control. |
| `http.url.addr:*api.census.gov*` | June 17–23 | 0 | 0 | Failed target control. |

Read every unnumbered row from [`feed-tests.jsonl`](_support/novelty/feed-tests.jsonl).
That ledger records exact queries, URLs, UTC retrieval times, and visible hit labels.
The 548-hit June result includes relay and direct submitted URLs.[17]
It MUST NOT be restated as 548 distinct county requests or 548 actors.[7][17]
The recent Jina result includes an unrelated September 18 Newspapers.com submission.[23]
Do not join it to June by relay syntax alone.

**urlscan:** Its documented public search excludes unlisted and private scans.[2]
The API returned 60 recent `task.domain:sec.gov` matches and no June matches.[30][31]
It also returned no June `domain:google.com` matches.[29]
The same broad domain returned results in September 3–4 tests; see [`feed-tests.jsonl`](_support/novelty/feed-tests.jsonl).
This observed access boundary prevents a June positive control here.[29]
Do not infer a formal retention period from this boundary.[3]
A published June AIHW urlscan result returned HTTP 403 through the result API.[37]
Its public page returned HTTP 429 during this pass.[38]
Manifold previously reported June 17–18 urlscan AIHW scans.[12]
The public API’s current June silence therefore does not refute those records.[12][29]
The API documentation warns that public-scan retention is not guaranteed.[3]

**GreyNoise:** Its Community API is an IP lookup, not a URL-path report search.[5]
GNQL supports observed HTTP paths, but this unauthenticated query returned HTTP 401.[4][32]
Standard GNQL describes a current 90-day aggregate; Recall provides historical time ranges.[6]
No June or recent GNQL hit count was obtained.[32]
No GreyNoise zero count is supported here.[32]

**urlquery limits:** The documented public search excludes reports unavailable to this user.[7]
Its service states that scan results have limited retention.[8]
Expensive searches can return partial results after a timeout.[7]
One broad June relay search stayed at “Searching..”; a one-day retry returned 94 hits.[27]
The public API returned HTTP 401 without an API key.[36]
The browser interface provided the paired results above.[17][18]
Indexing delay was not quantified by these sources.[7][8]
Private traffic, changed identifiers, and unsent scans remain outside this test.[2][7]

## Bounded novelty review

The [`search-ledger.jsonl`](_support/novelty/search-ledger.jsonl) records each public web query, result, and retrieval time.
It contains 37 item-specific novelty queries and 12 access/report queries.
The search universe included open-web indexing, GitHub-indexed results, named reports, and bounded Wayback CDX queries.
It did not include private reports, every social post, or every historical page version.[2][7]
Search snippets alone do not establish publication content.[7]
The findings below use retrieved report text and archive metadata where available.[9][12]
No exposed Census key was searched, tested, or copied into this file.

| Item | Novelty category | Bounded result |
| --- | --- | --- |
| **1. SEC Wayback burst** | Observation mentioned indirectly; exact burst impossible to establish exhaustively. | No prior report of the exact June 18 CDX burst was found. DeGraff documented county.json and major relays. Asymmetric named Wayback as a tool.[9][10] |
| **2. One June operation** | Impossible to establish exhaustively. | Existing reports discuss overlapping targets. Search found no independent proof that four clusters formed one operation.[9][12][14] |
| **3. Shadow relay layer** | **Already published**, except possible new per-host measurements. | DeGraff lists JQP, the AllOrigins clone, and cors.lol. Asymmetric lists JQP and the clone.[9][10] Lemino was not identified in those cited inventories. |
| **4. Census May 24 / retrieval** | Known incident already published; precise extension impossible to establish exhaustively. | Transluce documents June 16–22 key reuse and explicitly lacks a successful-response proof.[14] No searched prior page established the proposed May 24 record or June 17 outcome. |
| **5. AIHW June 18 Jina** | Earlier window already published; exact wrapper impossible to establish exhaustively. | Manifold published June 17–18 AIHW urlscan activity on September 25.[12] CDX independently lists one June 18 Jina-wrapped capture at 06:31:35 UTC.[33] |
| **6. Dormancy** | Wiki-silence assertion already published; exact feed test impossible to establish exhaustively. | A September 4 public post asserted wiki silence since July 2.[15] That assertion does not validate operational cessation. |

**Item 1 scope warning:** A fresh, uncollapsed June 18 Wayback CDX query returned 63 rows and 62 unique URLkeys.[34]
It returned 39 rows in the 20:00 UTC hour.[34]
The first indexed rows were at 02:23 UTC, before the brief’s claimed 14:52 first capture.[34]
The [brief](../discord-brief-2026-10-03.md) says 65 captures and 14:52 first capture.
These statements conflict under the stated query scope.[34]
The early rows include 404 statuses and a different `format` query.[34]
Do not merge all 63 rows into one nonce burst without checking query families.[34]
The redacted count and status breakdown are in [`archive-tests.jsonl`](_support/novelty/archive-tests.jsonl).
This is a scope warning, not a full re-audit of item 1.

**Item 3 prior-art detail:** DeGraff’s report counted 14,787 JQP mentions on Vanderbilt and 21,938 clone mentions.[10]
Those are different units and corpora from the brief’s proposed 14,341 county references.[10]
Do not equate their counts.[10]
The Register cited DeGraff’s report on September 10, before this brief.[11]
The public JQP repository also describes a general-purpose serverless proxy.[16]
“Never inventoried by anyone” is false for those named services.[9][10]

**Item 5 boundary:** The CDX row is an archive capture with status 200.[33]
It does not show Jina’s returned body, target receipt, actor identity, or common-operation membership.[33]
The exact timestamp and wrapper MAY be a narrower new archival observation.[33]
The earlier AIHW activity window itself is not new.[12]

**Item 6 prior-art boundary:** The September 4 post claims an end to wiki writes.[15]
Its publication is evidence of an earlier dormancy assertion, not evidence that the assertion is correct.[15]
A wiki-write cutoff cannot prove cessation on external targets or changed relays.[15]

## Open checks and disposition

Classify item 6 as **survives with narrower wording**.
Confidence is **high** that the three-feed cessation claim is unsupported.[29][32]
Confidence is **moderate** in the bounded urlquery county-string comparison.[17][18]
The visibility, retention, query-cost, and indexing limits prevent a complete absence census.[2][7][8]

To promote cessation, obtain known-good June and recent queries across comparable retained source records.
Define a stable fingerprint before searching.
Then test unlisted traffic, alternate relays, changed nonces, and other targets under authorized coverage.
Do not contact target services or test credentials for this review.

A skeptical researcher can independently conclude only this: selected public indexes differ between June and September–October.[17][18][29]
They cannot conclude that the same operation existed, remained stable, or stopped.

## Reproduction and evidence

- [`feed-tests.jsonl`](_support/novelty/feed-tests.jsonl): exact feed queries, URLs, HTTP status or UI labels, UTC retrieval time.
- [`archive-tests.jsonl`](_support/novelty/archive-tests.jsonl): Wayback CDX query URLs, status, bounded metadata, and failed attempts.
- [`search-ledger.jsonl`](_support/novelty/search-ledger.jsonl): item-specific novelty queries and search-engine result lists.
- [`publication-metadata.jsonl`](_support/novelty/publication-metadata.jsonl): live publication metadata and retrieval time.
- [`source-excerpts.md`](_support/novelty/source-excerpts.md): exact selected passages from fetched public pages.
- [`query-receipts.md`](_support/novelty/query-receipts.md): redacted query receipts generated from the JSONL ledgers.
- [`citations.json`](_support/novelty/citations.json): source IDs and attached excerpts.

Do not treat a search-engine result count as a census of publications.
Do not infer cessation from missing hits in a partial public index.

## Sources

[1] https://urlscan.io/docs/search — urlscan-search-docs.md
[2] https://urlscan.io/docs/api — urlscan-api-docs.md
[3] https://urlscan.io/docs/faq — urlscan-faq.md
[4] https://docs.greynoise.io/docs/using-the-greynoise-query-language-gnql — greynoise-gnql-docs.md
[5] https://docs.greynoise.io/docs/using-the-greynoise-community-api — greynoise-community-docs.md
[6] https://docs.greynoise.io/docs/recall — greynoise-recall.md
[7] https://urlquery.net/help/search — urlquery-search-docs.md
[8] https://urlquery.net/about — urlquery-about.md
[9] https://www.asymmetricsecurity.com/newsroom/rogue-agents-investigation-initial-findings — asymmetric-findings.md
[10] https://www.kennethdegraff.com/swarm — degraff-swarm.md
[11] https://www.theregister.com/ai-and-ml/2026/09/10/openais-website-hijacking-swarm-reached-far-further-than-we-thought/5295644 — register-20260910.md
[12] https://www.manifold.security/blog/ai-agents-urlscan-aihw-government-data — manifold-aihw.md
[13] https://transluce.org/agent-activity — transluce-agent-activity.md
[14] https://transluce.org/us-canada-gov — transluce-us-canada-gov.md
[15] https://thecolony.cc/post/a7beb729-c578-4ee3-8b88-82a0c6b6603e — colony-census-post.md
[16] https://github.com/sighrobot/jqp — jqp-github.md
[17] https://urlquery.net/search?q=http.url.addr%3A%2Acounty.json%2A%20AND%20date%3A%5B2026-06-17%20TO%202026-06-19%5D&type=reports — urlquery-county-june
[18] https://urlquery.net/search?q=http.url.addr%3A%2Acounty.json%2A%20AND%20date%3A%5B2026-09-04%20TO%202026-10-04%5D&type=reports — urlquery-county-recent
[19] https://urlquery.net/search?q=http.url.addr%3A%2Aaihw.gov.au%2A%20AND%20date%3A%5B2026-06-17%20TO%202026-06-23%5D&type=reports — urlquery-aihw-june
[20] https://urlquery.net/search?q=http.url.addr%3A%2Aaihw.gov.au%2A%20AND%20date%3A%5B2026-09-04%20TO%202026-10-04%5D&type=reports — urlquery-aihw-recent
[21] https://urlquery.net/search?q=http.url.addr%3A%2Ajqp.vercel.app%2A%20AND%20date%3A%5B2026-06-17%20TO%202026-06-23%5D&type=reports — urlquery-jqp-june
[22] https://urlquery.net/search?q=http.url.addr%3A%2Ajqp.vercel.app%2A%20AND%20date%3A%5B2026-09-04%20TO%202026-10-04%5D&type=reports — urlquery-jqp-recent
[23] https://urlquery.net/search?q=http.url.addr%3A%2Ar.jina.ai%2A%20AND%20date%3A%5B2026-09-04%20TO%202026-10-04%5D&type=reports — urlquery-jina-recent
[24] https://urlquery.net/search?q=http.url.addr%3A%2Ar.jina.ai%2A%20AND%20date%3A%5B2026-06-17%20TO%202026-06-23%5D&type=reports — urlquery-jina-june
[25] https://urlquery.net/search?q=http.url.addr%3A%2Aapi.cors.lol%2A%20AND%20date%3A%5B2026-06-17%20TO%202026-06-19%5D&type=reports — urlquery-cors-june
[26] https://urlquery.net/search?q=http.url.addr%3A%2Aapi.cors.lol%2A%20AND%20date%3A%5B2026-09-04%20TO%202026-10-04%5D&type=reports — urlquery-cors-recent
[27] https://urlquery.net/search?q=http.url.addr%3A%2Aallorigins.hexlet.app%2A%20AND%20date%3A%5B2026-06-18%20TO%202026-06-19%5D&type=reports — urlquery-allorigins-june
[28] https://urlquery.net/search?q=http.url.addr%3A%2Aallorigins.hexlet.app%2A%20AND%20date%3A%5B2026-09-04%20TO%202026-10-04%5D&type=reports — urlquery-allorigins-recent
[29] https://urlscan.io/api/v1/search/?q=domain%3Agoogle.com+AND+date%3A%5B2026-06-18+TO+2026-06-19%5D&size=3 — urlscan-june-google
[30] https://urlscan.io/api/v1/search/?q=task.domain%3Asec.gov+AND+date%3A%5B2026-09-04+TO+2026-10-04%5D&size=10 — urlscan-recent-sec
[31] https://urlscan.io/api/v1/search/?q=task.domain%3Asec.gov+AND+date%3A%5B2026-06-18+TO+2026-06-19%5D&size=10 — urlscan-june-sec
[32] https://api.greynoise.io/v2/experimental/gnql?query=raw_data.http.path%3A%22%2Acounty.json%2A%22&size=1 — greynoise-401
[33] https://web.archive.org/cdx/search/cdx?url=r.jina.ai%2Fhttp%3A%2F%2Fhttps%3A%2F%2Fwww.aihw.gov.au%2Fgetmedia%2F57e4c61f%2A&from=20260618&to=20260618&output=json&fl=timestamp%2Curlkey%2Cstatuscode&limit=10 — wayback-aihw
[34] https://web.archive.org/cdx/search/cdx?url=sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260618&to=20260618&output=json&fl=timestamp%2Curlkey%2Coriginal%2Cdigest%2Cstatuscode&limit=200 — wayback-county
[35] https://web.archive.org/cdx/search/cdx?url=transluce.org%2Fagent-activity&from=20260901&to=20261003&output=json&fl=timestamp%2Coriginal%2Cstatuscode&filter=statuscode%3A200&collapse=timestamp%3A8&limit=30 — wayback-report-sep24
[36] https://api.urlquery.net/public/v1/search/reports/?query=http.url.addr%3A%2Acounty.json%2A+AND+date%3A%5B2026-06-18+TO+2026-06-19%5D — urlquery-api-401
[37] https://urlscan.io/api/v1/result/019ed827-0471-746c-aa31-8da7d1e6f6ae — urlscan-result-403
[38] https://urlscan.io/result/019ed827-0471-746c-aa31-8da7d1e6f6ae — urlscan-public-429
