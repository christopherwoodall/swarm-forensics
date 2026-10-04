# 07 — Strict and interpretive chronologies

## Strict chronology

The complete selected-observation table contains 74 rows.
See [strict-chronology.csv](_support/strict-chronology.csv).
It includes every retained SEC CDX row and selected cross-cluster boundary records.
It is not a census of all activity.

Every row states its clock type, raw reference, evidence level, linkage limit, and confidence.
Unknown source, discovery-precision, or publication times remain empty.
The following table summarizes that CSV.

| UTC | Observed event | Unit and primary reference | Evidence ceiling |
| --- | --- | --- | --- |
| May 24, 07:08:39.335 | Malformed ACS5 GET receives HTTP 302 | First browser transaction, report `87465efc-fc5e-484a-8089-b99f6981f575` [2] | Target response; no ACS data |
| May 24, 07:08:41.987 | Second matching GET receives HTTP 302 | Report `7d967df7-fcf5-4df1-927b-2642039a7b84` [3] | Separate report, not separate authenticated actor |
| June 17, 02:39:07 | Direct Census file archived | B16001 direct capture [7] | Archive holds data; no relay linkage |
| June 17, 02:59:07 | Jina wrapper archived | Empty Markdown content [4] | No requested file content |
| June 17, 03:02:12 | AllOrigins wrapper archived | Nginx error page [5] | Failed wrapper response |
| June 17, 03:03:01 | CorsProxy wrapper archived | Free-use restriction [6] | Failed wrapper response |
| June 17, 05:26:13 | Second direct Census file capture | Same decoded file hash [7] | Separate archive observation |
| June 18, 02:23:00 | First SEC prefix CDX entry | Indexed 404 [1] | Capture mechanism unknown |
| June 18, 04:23:09.763 | First exported county-substring HTTP entry | SEC HTTP CSV, M1 | Browser request record |
| June 18, 06:31:35 | Jina/AIHW doubled-scheme capture | Security-check text [8] | No diagnosis workbook |
| June 18, 06:59:25 | First indexed SEC 200 JSON row | CDX [1] | Index class, not agent receipt |
| June 18, 14:10:56 | First scoped wiki county-file addition | `probier~RecentChanges@40`, source time [17] | Wiki artifact exists |
| June 18, 14:52:28 | First bare-decimal SEC query capture | CDX [1] | Not the day's first capture |
| June 18, 17:32:02 | First `x=0.<digits>` SEC capture | CDX [1] | Grammar only |
| June 18, 20:13:42–20:21:25 | Peak SEC archive interval | 39 index entries [1] | No submitter identity |
| June 18, 23:27:19.644 | Last exported county-substring HTTP entry | SEC HTTP CSV, M1 | Not operation termination |

M1 means [parent-measurements.json](_support/parent-measurements.json).
The source ZIP and member hashes are recorded there.

## Timing corrections

The brief's “wiki before first capture” claim confuses a nonce subtype with the whole query result.
The earliest SEC archive entry precedes the first matching wiki edit by 11 hours, 47 minutes, 56 seconds.[1][17]
The first bare-decimal capture follows that wiki edit by 41 minutes, 32 seconds.[1][17]
Both statements can hold because they refer to different populations.

The 39-entry archive peak lasts 463 seconds.[1]
Its median adjacent gap is ten seconds.[1]
An hourly count of 39 does not mean evenly spaced 90-second saves.
The first/last timestamp span and adjacent-gap statistics are more informative.

The SEC wiki count includes 250 matching revisions within that peak interval.[1][17]
This is genuine temporal overlap in the inspected data.
It does not identify who initiated archive captures.

## Interpretive chronology

This section contains hypotheses, not additional observed events.

| Proposed sequence | What permits the hypothesis | Why it remains unproved |
| --- | --- | --- |
| Census Jina → AllOrigins → CorsProxy retries | Same static-file path; close archive times | No common initiator; all three fail to return data |
| Wiki publication → SEC archive submissions | Some exact URL references and later temporal overlap | Earliest archive activity precedes wiki activity; no save-origin metadata |
| SEC browser failures → wiki relay experiments | Same target family across an overlapping day | No captured transfer between a specific report and editor |
| AIHW June 18 → pharmaceutical case June 20–21 | Same agency | Different resource and task; returned block page |
| June cluster → cessation | Recent query absence | Failed controls and incomplete public visibility |

Do not draw a causal arrow for any row in this table.
The [typed graph](_support/operation-graph.json) keeps observation and hypothesis edges separate.

## Publication and discovery chronology

The June timestamps above are not report-publication dates.
Transluce's relevant articles appeared September 23 and September 30.[9][10]
Manifold's September 25 account already reported June 17–18 AIHW activity.[13]
The original brief and matrix are dated October 3.
This review's primary replays and index lookups occurred October 4 UTC.

A later publication can report an earlier event.
An archive capture predating publication does not prove an independent investigator or agent initiated it.

## Sources

[1] https://web.archive.org/cdx/search/cdx?url=sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260618&to=20260618&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cdigest%2Cstatuscode%2Cmimetype%2Clength%2Cfilename%2Coffset
[2] https://urlquery.net/report/87465efc-fc5e-484a-8089-b99f6981f575 — May24 report A
[3] https://urlquery.net/report/7d967df7-fcf5-4df1-927b-2642039a7b84 — May24 report B
[4] https://web.archive.org/web/20260617025907id_/https://r.jina.ai/http://www2.census.gov/programs-surveys/acs/summary_file/2022/table-based-SF/data/1YRData/acsdt1y2022-b16001.dat — Wayback Jina replay
[5] https://web.archive.org/web/20260617030212id_/https://api.allorigins.win/raw?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback AllOrigins replay
[6] https://web.archive.org/web/20260617030301id_/https://corsproxy.io/?url=https%3A%2F%2Fwww2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat — Wayback CorsProxy replay
[7] https://web.archive.org/cdx/search/cdx?url=www2.census.gov%2Fprograms-surveys%2Facs%2Fsummary_file%2F2022%2Ftable-based-SF%2Fdata%2F1YRData%2Facsdt1y2022-b16001.dat&from=20260617&to=20260617&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cstatuscode%2Cmimetype%2Cdigest%2Clength — Wayback Census static-file CDX
[8] https://web.archive.org/web/20260618063135id_/https://r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/Principal-Diagnosis-cube_2014-15.xlsx.aspx — Wayback AIHW replay
[9] https://transluce.org/us-canada-gov — Transluce Census
[10] https://transluce.org/agent-activity — Transluce AIHW
[13] https://www.manifold.security/blog/ai-agents-urlscan-aihw-government-data — manifold-aihw.md
[17] https://collusion.wiki/explorer/download.html
