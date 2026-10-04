# Item 1 — SEC `county.json` Wayback burst

## Decision

**Disposition: C — split the observation from mechanism and attribution.**
The original brief claims 65 captures, 61 identical digests, on-demand agent saving, and no prior publication.
The current public index supports a smaller, narrower observation.[1][2]

**Strongest defensible wording:** Wayback indexed 63 entries for the SEC file on 2026-06-18.[1]
Forty-nine entries carry one of two decimal nonce grammars.[1]
Thirty-nine entries fall between 20:13:42 and 20:21:25 UTC.[1]
This is an action-shaped archival trace, not a verified agent action.

**Claim level: 1 (action-shaped trace).**
Confidence is high for the bounded index counts and low for capture-origin inference.
Do not promote this item to level 2, 5, or 6 without independent evidence.
The strongest rejected wording is **“verified agent-driven on-demand saving, not a crawler.”**
Archive entries do not identify the initiator, the collection route, or a known agent population.[1][6]

## Reconstructed units

| Unit | No collapse | `collapse=urlkey` | Interpretation |
| --- | ---: | ---: | --- |
| CDX index entries | 63 | 62 | One row disappears. |
| Unique original URL strings | 62 | 62 | One exact URL has two timestamps. |
| Unique URL keys | 62 | 62 | One key has a revisit. |
| Unique capture timestamps | 63 | 62 | Each raw row has a distinct UTC second. |
| Unique content digests | 2 | 2 | A repeated digest is not a repeated request count. |
| `VABBDDDTZS2COG3DDYVIWHVX7TDH7OYH` rows | 60 | 59 | Includes one `warc/revisit` row. |
| `BJBCG6F62WUWNLUF5UPWWDMMOKB4V7GA` rows | 3 | 3 | All three index as HTTP 404 HTML. |
| HTTP 200 JSON rows | 59 | 59 | These are archive index classifications. |
| HTTP 404 HTML rows | 3 | 3 | Do not infer client intent from errors. |
| `warc/revisit` rows | 1 | 0 | Status code is `-`. |

The raw first timestamp is 02:23:00 UTC; the last is 20:21:25 UTC.[1]
The collapsed result omits the 16:51:10 revisit for the bare URL.[1][2]
It retains that URL's earlier 14:19:37 HTTP 404 row.[1][2]
Thus, collapse changes the total little but can hide a later response class.
The raw 63 entries do not reproduce the brief's 65 entries.[1]
The raw common-digest count is 60, not the brief's 61.[1]
That digest covers 95.24% of raw rows.[1]
Index mutation or a different historic query remains possible; neither is demonstrated.[1][2]
Identical index digests suggest repeated archived content, not 60 independently verified byte-identical replays.[1]
Indexed `length` values vary, and public `filename` and `offset` values are empty.[1]
A bounded replay returned JSON for the revisit; two peak replays encountered connection refusals.
See the replay limit in [the retrieval table](_support/sec/retrieval-table.md).

| Query shape, with values redacted | Raw entries | Decimal digit lengths |
| --- | ---: | --- |
| `?x=0.<digits>` | 41 | 15: 5; 16: 27; 17: 7; 18: 1; 19: 1 |
| `?0.<digits>` | 8 | 15: 1; 16: 4; 17: 3 |
| malformed `?x0.<digits>` | 1 | 17: 1 |
| `?x=<integer>` | 5 | One digit each |
| Other named query shapes | 6 | Names only in the redacted CSV |
| No query | 2 | One 404 and one revisit |

These shapes total 63 raw entries.[1]
Only seven entries match the brief's literal `?x=0.<17 digits>` grammar.[1]
The broader `?x=0.<digits>` family contains 41 entries.[1]
All 41 family values are distinct in this result set.[1]
The separate eight bare-decimal values are also distinct.[1]
The decimal forms resemble generic random-number serialization; they do not identify a library.[8]
No source code or request headers establish `Math.random()` as the generator.

## Strict chronology and alignment

| UTC, 2026-06-18 | Observed unit | Raw reference | Evidence class |
| --- | --- | --- | --- |
| 02:23:00–02:23:26 | Two SEC CDX 404 entries | `cdx-events-redacted.csv`, timestamps | Archive index [1] |
| 06:59:25 | First indexed SEC 200 JSON entry | Same table | Archive index [1] |
| 14:10:56 | First wiki added-text reference to `county.json` | `counts.json`, first wiki raw-ref hash | Wiki revision; `reqlog`, ±1 second [5] |
| 14:19:37 | Bare SEC URL indexes as 404 | CDX table, timestamp | Archive index [1] |
| 14:39:38 | SEC integer-query URL indexes as 200 | CDX table, timestamp | Archive index [1] |
| 14:52:28 | First bare-decimal SEC capture | CDX table, timestamp | Archive index [1] |
| 16:51:10 | Bare URL indexes as `warc/revisit` | CDX table, timestamp | Archive index [1] |
| 17:32:02 | First `?x=0.<digits>` capture | CDX table, timestamp | Archive index [1] |
| 20:00:15 | First wiki added-text reference in the 20:00 hour | Wiki CSV, timestamp | Wiki revision [5] |
| 20:13:42–20:21:25 | 39 SEC CDX entries | CDX CSV, timestamp range | Archive index [1] |
| 20:59:46 | Last wiki added-text reference in the 20:00 hour | Wiki CSV, timestamp | Wiki revision [5] |

The first archive entry predates the first wiki reference by 11 hours, 47 minutes, 56 seconds.[1][5]
The first bare-decimal capture follows that wiki reference by 41 minutes, 32 seconds.[1][5]
The archive's peak 39 entries occupy seven minutes, 43 seconds.[1]
This gives 5.05 entries per minute across the observed peak span.[1]
Their median adjacent gap is ten seconds; the full-day median is eleven seconds.[1]
The wiki has 1,759 matching added-text revisions in the 20:00 hour.[5]
Exactly 250 matching wiki revisions fall within the archive's 20:13:42–20:21:25 window.[1][5]
These units are wiki revisions and CDX entries, not requests by identified agents.
Temporal overlap does not establish that wiki activity caused the archive captures.

The wiki count uses inserted or replaced text, not inherited full-page copies.[5]
The first revision records `time_grade=reqlog`, `uncertainty_seconds=1`, and `archived_at=14:11:46`.
Treat its `time=14:10:56` as source time, not Wayback archive time.
The ZIP export and its expanded revision checksum are recorded in [the retrieval table](_support/sec/retrieval-table.md).[5]
The brief's 14:52 first-capture claim omits three pre-wiki entries and four other pre-14:52 entries.[1][5]
It describes the first bare-decimal capture, not the first archival capture.

## Adversarial controls and mechanism

The June prefix control has one plain-URL entry on June 7 and 63 June 18 entries.[3]
It has no entries on June 17 or 19 within this query scope.[3]
That one earlier row is too small to establish a normal rate.[3]
A sibling SEC file, `regcf.json`, has four June 18 entries.[4]
Three sibling entries use bare 16-digit decimal query forms near 14:52 UTC.[4]
This sibling is task-related; it is not an unrelated human-traffic control.
It shows that the decimal shape is not unique to `county.json`.[1][4]
An unrelated, dated human baseline remains missing from these two controls.[3][4]

Seven distinct SEC original URLs appear literally in wiki added text on June 18.[1][5]
One bare URL appeared there at 14:10:56, before its 14:19:37 archival entry.[1][5]
No exact decimal-nonce original appears in this local wiki added-text search.[1][5]
These checks use literal strings; encoded or alternate-scheme variants remain uncounted.[1][5]
The wiki also contains later Wayback links for this file, but their embedded dates target older years.[5]
No matching added-text revision contains a `web.archive.org/save/` string in this search.[5]

A blind crawler cannot guess arbitrary query values merely from the SEC base URL.
That does **not** exclude crawler discovery through HTML, JavaScript, links, feeds, logs, referrers, or submitted URLs.
A browser extension or another archiving integration can also submit a URL.[7]
Save Page Now is one possible path, not a demonstrated path.[7]
CDX provides timestamps, URL keys, digests, MIME types, and response classes.[1][6]
It does not provide a public source IP, user-agent, referrer, submitter, or job identifier here.[1][6]
The empty WARC location fields prevent a record-level provenance check here.[1]
Repeated index entries can reflect distinct captures, redirects, revisits, or index handling.[1][6]
The one explicit revisit disproves an assumption that every row is a separate new-content save.[1]
No target-side SEC log was examined.
Do not convert 63 archive entries into 63 agent requests or 63 SEC-origin hits.

## Attribution, novelty, and rejected claims

Transluce published the June 18 SEC crowdfunding workflow before this review.[9]
The public wiki-analysis repository also documented the SEC file as a task source.[10]
RubyGems and shortener investigations discussed the same SEC file.[11][12]
These sources make the file and its workflow previously published subjects.
The bounded search found no earlier enumeration of this exact Wayback burst.
It cannot establish that nobody published the Wayback observation elsewhere.
Classify novelty as **not found in searched publications; globally unresolved**.
See the exact search universe and limits in [the retrieval table](_support/sec/retrieval-table.md).

Reject “65 verified captures” and “61 byte-identical copies” for the current CDX snapshot.[1]
Reject “41 exact 17-digit `x` nonces”; seven entries meet that precise grammar.[1]
Reject “the wiki started before the first Wayback capture”; the first capture is much earlier.[1][5]
Reject “a crawler could not discover these URLs” as an absolute exclusion.
Reject “agent-driven” and “same tooling family” as conclusions from the captures alone.
No shared exact decimal URL, initiator metadata, or handoff joins these archival rows to a known actor.
No archive capture proves that an agent read or used the preserved JSON.

**Unresolved alternatives:** on-demand submissions, crawler discovery, browser saves, third-party integrations, and later indexing remain possible.
A capture-source log would discriminate the submission paths.
Dated first appearances of exact nonce URLs would test crawler discovery.
Authorized origin or CDN logs could test target receipt.
A larger unrelated human baseline could test grammar specificity.
Do not initiate new saves or credential tests for these checks.

**Independent-reader test:** A skeptical reader would find a tight archival burst and a concurrent wiki topic.
The reader would not identify the archive submitter or merge this burst into an agent operation.

## Evidence paths and reproducibility

- [Redacted CDX entry table](_support/sec/cdx-events-redacted.csv): 63 entry rows.
- [Redacted wiki added-text table](_support/sec/wiki-county-added-redacted.csv): 4,132 revision rows.
- [Counts and raw-reference hashes](_support/sec/counts.json): 63 CDX entries and 4,132 matching wiki revisions.
- [Exact queries, response hashes, controls, and replay limits](_support/sec/retrieval-table.md).
- [Citation ledger](_support/sec/citation-ledger.json): stable source-ID mapping.

The CDN-visible CDX results were retrieved on 2026-10-04 UTC.
The cited publication dates are separate from the June source and archive times.
The archive query matches one normalized SEC path prefix, not every SEC request or wrapper host.
Raw CDX rows and replay bodies remain outside this directory.

## Sources

[1] https://web.archive.org/cdx/search/cdx?url=sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260618&to=20260618&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cdigest%2Cstatuscode%2Cmimetype%2Clength%2Cfilename%2Coffset
[2] https://web.archive.org/cdx/search/cdx?url=sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260618&to=20260618&output=json&collapse=urlkey&fl=timestamp%2Coriginal%2Curlkey%2Cdigest%2Cstatuscode%2Cmimetype%2Clength%2Cfilename%2Coffset
[3] https://web.archive.org/cdx/search/cdx?url=www.sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260601&to=20260630&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cdigest%2Cstatuscode%2Cmimetype%2Clength&limit=1000&showResumeKey=true
[4] https://web.archive.org/cdx/search/cdx?url=www.sec.gov%2Ffiles%2Fregcf.json&matchType=prefix&from=20260618&to=20260618&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cdigest%2Cstatuscode%2Cmimetype%2Clength&limit=1000
[5] https://collusion.wiki/explorer/download.html
[6] https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md?plain=1
[7] https://help.archive.org/help/save-pages-in-the-wayback-machine
[8] https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random
[9] https://transluce.org/us-canada-gov
[10] https://github.com/JoshuaDavid/WikiAgentSwarmInvestigation/tree/main/tasks/sec-regcf-ma-cache
[11] https://rubyhack.ai
[12] https://www.kennethdegraff.com/swarm
