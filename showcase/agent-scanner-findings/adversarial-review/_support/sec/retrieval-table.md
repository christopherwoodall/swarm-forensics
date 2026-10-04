# SEC item 1: retrieval and redaction register

All retrievals used public, read-only endpoints.
All network retrievals occurred on 2026-10-04 UTC.
The citation ledger uses the local 2026-10-03 date.
Source IDs refer to `citation-ledger.json`.

## CDX queries

Send each query to `https://web.archive.org/cdx/search/cdx` with `curl -G --data-urlencode`.
Use `output=json` for each query.
The raw responses remain in scratch.
The repository stores only redacted derivations.

| Query | Source | `url` parameter | Dates, scope, fields, limit | HTTP; bytes | Raw response SHA-256 | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | [1] | `sec.gov/files/county.json` | `matchType=prefix`; `from=20260618`; `to=20260618`; `fl=timestamp,original,urlkey,digest,statuscode,mimetype,length,filename,offset`; no `collapse`; no explicit `limit` | 200; 12,812 | `aaf3ac9de6352d01924c7ebebfedb6984b2e7699589be62205141feb4b7d85fa` | 63 rows |
| Q2 | [2] | same | Q1 fields and bounds; `collapse=urlkey`; no explicit `limit` | 200; 12,652 | `dca671a60f22dcea059f3bab38c18b852a585c4f563b57df747ba86ae103cb71` | 62 rows |
| Q3 | [3] | `www.sec.gov/files/county.json` | `matchType=prefix`; `from=20260601`; `to=20260630`; `fl=timestamp,original,urlkey,digest,statuscode,mimetype,length`; `limit=1000`; `showResumeKey=true` | 200; 12,319 | `f99f57e67f9d5f81b9b6e7ec7be8e52a8a3227087277e69c0eb23992eca4302c` | 64 rows; no resume key; one June 7 row |
| Q4 | [4] | `www.sec.gov/files/regcf.json` | Q3 scope and fields; `from=to=20260618`; `limit=1000`; no resume flag | 200; 808 | `f54c5d4a59099e2e0cb015fcc0d1be117fffe5f878330e00bee6dbb196e2cf1a` | Four sibling-file rows |
| Q5 | supplemental | `www.sec.gov/files/county.json` | Q4 date and fields; `limit=1000`; `showResumeKey=true` | 200; 12,162 | `94c02ccff0124f21879272901526ccb06b6854305d1b5a125247375e49087bbc` | Same 63 timestamps as Q1; no resume key |
| Q6 | supplemental | `www.sec.gov/files//county.json` | Q4 date and fields; `limit=1000` | 200; 12,162 | `94c02ccff0124f21879272901526ccb06b6854305d1b5a125247375e49087bbc` | Same 63 records; path normalized |
| Q7 | supplemental | `www.sec.gov/files/regcf.json` | Q3 date and fields; `limit=1000`; no resume flag | 200; 808 | `f54c5d4a59099e2e0cb015fcc0d1be117fffe5f878330e00bee6dbb196e2cf1a` | Same four records as Q4 |

Q1 and Q2 returned empty `filename` and `offset` values in all rows.
These public fields do not reveal a WARC record address or capture initiator.
Q3 and Q5 show no truncation within these narrow result sets.
These results do not establish global Wayback coverage.
A wider domain-wide query was not made.

## Wiki source and method

Read `colette-research/sources/rubygems-wiki-collusion/full-wiki-logs.zip!revisions.jsonl` locally.
The ZIP SHA-256 is `eb68aa12d26bf189d8bfc4ce47f4d8af66ae5ba7ebbadd429738297a3cbb25ae`.
The expanded `revisions.jsonl` SHA-256 is `60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793`.
The second checksum matches the publisher's checksum on source [5].
Stream all 14,591 revision rows one at a time.
Keep rows whose `time` starts with `2026-06-18`.
Extract each `body.split('\n')[b0:b1]` for `insert` and `replace` hunks.
Search the added text for case-insensitive `county.json`.
Do not count inherited body text as a new mention.
Hash `rev_id` with SHA-256 to create stable, redacted raw references.
Compare unredacted CDX `original` strings in memory against added text.
Never export those original strings or wiki page bodies.

## Replay limit

Four bounded `id_` replay attempts used unredacted Q1 URLs in memory.
The 14:19:37 record returned HTTP 404 HTML from Wayback.
The response held 53,435 bytes and SHA-256 `ee242e8e000b149b3b700c2d82cb051d76e7c146a13ff52b3d7ce4e3acd6d06e`.
The 16:51:10 revisit replay returned HTTP 200 JSON.
The response held 18,032 bytes and SHA-256 `b8184b57cb5239935ab4f06d1916ff5de18c1a94add901d24120ee0a0cef7b3c`.
The 20:13:42 and 20:13:48 replays failed with connection refused.
Do not treat the 404 replay as an independently verified SEC-origin response.
Do not treat the successful revisit replay as evidence of its requester.
No `save/` endpoint was called.

## Novelty search scope

Use `web_search` with limit 10 unless stated otherwise.
Search `"county.json" "Wayback" agents June 2026`.
Search `"county.json" "2026061820" "archive.org"`.
Search `"sec.gov/files/county.json" "archive" "June 18" 2026`.
Search `"county.json" "save page now" SEC 2026 agent`.
Search `"web.archive.org/web/20260618" "county.json"`.
Search the exact CDX digest and one exact nonce value; do not retain the nonce.
Search `site:github.com/JoshuaDavid/WikiAgentSwarmInvestigation "county.json" "wayback"`.
Search `site:collusion.wiki county.json wayback archive June 18`.
Search `site:transluce.org/us-canada-gov county.json June 18 SEC` with limit 5.
Read the indexed publications [9], [10], [11], and [12].
This search does not cover all social posts, private reports, or historic page versions.

## Durable evidence units

`counts.json` records the summary and first fifteen redacted wiki raw references.
`cdx-events-redacted.csv` has one row per Q1 CDX entry.
`wiki-county-added-redacted.csv` has one row per matching wiki revision.
`citation-ledger.json` maps report citations to public URLs.
The CSV files contain hashes, times, fields, and counts.
They contain no original nonce URLs, page bodies, credentials, or personal identifiers.
