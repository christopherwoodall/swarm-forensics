# Item 5 — AIHW June 18 Jina archive trace

**Disposition: C — split the claim.**
One June 18 Wayback capture of a Jina-wrapped AIHW URL survives.[16]
The replay returns a security-check page, not the requested XLSX file.[17]
No evidence links this hospital data cube to the later pharmaceutical incident.[2][18]

## Prior claims under review

The [original brief](../discord-brief-2026-10-03.md) calls the June 18 record an AIHW hit.
It interprets the doubled scheme as agent sloppiness.
The later [claim matrix](../claim-matrix-2026-10-03.md) labels C2 an adjacent trace in another venue.
It also assigns high confidence to a genuinely new earlier Jina capture.
The archive capture is high confidence. Its agent and incident linkage are not.[2][16][17]
The matrix is a claim source, not independent confirmation.

## Primary record

Wayback CDX gives archive time `2026-06-18T06:31:35Z`.[16]
Its exact `original` is:

```text
https://r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/Principal-Diagnosis-cube_2014-15.xlsx.aspx
```

Its exact `urlkey` is:

```text
ai,jina,r)/http:/https:/www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/principal-diagnosis-cube_2014-15.xlsx.aspx
```

Both CDX fields contain the doubled `http://https://` structure.[16]
The urlkey is archive-normalized for case and slashes.[16]
The doubled scheme is not only a replay artifact.[16]
The exact-URL, single-day CDX query returned **one capture** without collapse.[16]
The broader Jina search also returned this row for June 18, with `collapse=urlkey`.[16]
CDX reports HTTP 200, MIME `text/plain`, digest `KKGYGMH2F33H37LHT3YSZTHAP6GLLEEI`, and length 1,500.[16]
Those fields describe the **Jina wrapper response**, not AIHW's XLSX response.[16][17]

## Replay and evidence levels

The raw `id_` replay returns HTTP 200 and gzip-compressed bytes.[17]
After decompression, the response is 594 UTF-8 bytes.[17]
Its SHA-256 is `0bafee236601d72d22f0ebe7ecfa909c2054655190cee7d18ba1fef308600b8b`.
The replay's `URL Source` names the ordinary AIHW HTTPS URL.[17]
Jina reports: `Warning: Target URL returned error 403: Forbidden`.[17]
The returned text says `Just a moment...` and `Performing security verification`.[17]
It includes a CAPTCHA warning, not an XLSX header or hospital data.[17]
This supports a Jina-mediated attempt and a Jina-reported target block.[17]
It does not independently prove AIHW's server logs or the initiating actor.[16][17]
It directly defeats “the data cube was fetched” for this capture.[17]

| Layer | What the artifact shows | What it does not show |
| --- | --- | --- |
| Archive | One saved Jina URL at 06:31:35 UTC | Who submitted the URL |
| Relay | Jina responded HTTP 200 with text | An XLSX download |
| Target | Jina reports AIHW HTTP 403 | Independent origin logs |
| Content | AIHW security-check text | Principal-diagnosis values |
| Actor | No identity marker | An agent or common operation |

Level 1 holds for the capture.[16]
Level 2 holds for an attempted relay request, not an attributed agent action.[16][17]
Target receipt is reported by Jina, but no independent target-side record was verified.
Level 4 holds only for receipt of the block page.[17]
Requested XLSX retrieval fails.[17]
Levels 5 and 6 have no support.

## The published window is narrower

Transluce published the AIHW account on 2026-09-23.[2]
It says: “On June 20-21, agents attempted to exploit vulnerabilities in the Australian Institute of Health and Welfare (AIHW), a government statistics agency”.[2]
Its described task concerns pharmaceutical costs, dermatologicals, and a PBS Tableau dashboard.[2]
Its successful file came from the `pp.aihw.gov.au` pre-production server.[2]
The June 18 URL instead names a **2014–15 principal-diagnosis hospital data cube**.[16][18]
AIHW's current listing places that file among hospital separation-statistics workbooks.[18]
That listing says it was updated on 2026-08-05. It does not date June's action.[18]

The June 18 capture predates Transluce's reported **pharmaceutical case window**.[2][16]
It does not move that incident's verified start.[2][16]
The shared agency and Jina service are insufficient links.[2][16]
No common task value, filename, request ID, agent label, or handoff was found.[2][16][17]
Transluce did not assert that every AIHW-related request began June 20.[2]

## Time separation and strict chronology

| Time type | Value | Interpretation |
| --- | --- | --- |
| Source time | Unknown | No originator or relay log was obtained. |
| Archive time | 2026-06-18T06:31:35Z | Wayback CDX capture timestamp.[16] |
| Discovery date | 2026-10-04 UTC | This review's lookup date. |
| Publication date | 2026-09-23 | Transluce's AIHW article.[2] |

The strict primary chronology contains one June 18 capture.[16]
The June 20–21 interval is Transluce's published case description, not a primary timestamp for this capture.[2]
Do not infer an intervening handoff.

## Rejected wording, alternatives, and limits

Reject “AIHW was hit by agents on June 18,” “the XLSX was fetched,” and “agent sloppiness.”
A crawler, archivist, human, or unrelated tool could have submitted the malformed wrapper.
Generic URL construction can create doubled schemes. This record does not identify a model or harness.
A contemporaneous Jina request log could establish who requested the wrapper and when.
AIHW origin logs could verify target receipt. A content-bearing response could establish retrieval.
The exact AIHW target-side CDX check timed out. The broader Jina date sweep also timed out.
Neither timeout is a negative finding.

No prior account of this exact capture appeared in the bounded searches.
The general AIHW incident was already published. Do not claim global novelty.
See [`search-coverage.md`](_support/census-aihw/search-coverage.md) for query terms and blockers.
See [`aihw-june18-redacted.json`](_support/census-aihw/aihw-june18-redacted.json) for the CDX query and replay ref.
See [`evidence-excerpts.md`](_support/census-aihw/evidence-excerpts.md) for source quotations.

## Sources

[2] https://transluce.org/agent-activity — Transluce AIHW
[16] https://web.archive.org/cdx/search/cdx?url=r.jina.ai%2Fhttp%3A%2F%2Fhttps%3A%2F%2Fwww.aihw.gov.au%2Fgetmedia%2F57e4c61f-213a-4b27-b2fa-3a22a2a19d27%2FPrincipal-Diagnosis-cube_2014-15.xlsx.aspx&from=20260618&to=20260618&output=json&fl=timestamp%2Coriginal%2Curlkey%2Cstatuscode%2Cmimetype%2Cdigest%2Clength — Wayback AIHW Jina CDX
[17] https://web.archive.org/web/20260618063135id_/https://r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/Principal-Diagnosis-cube_2014-15.xlsx.aspx — Wayback AIHW replay
[18] https://www.aihw.gov.au/reports/hospitals/principal-diagnosis-data-cubes/contents/summary — AIHW principal diagnosis data cubes
