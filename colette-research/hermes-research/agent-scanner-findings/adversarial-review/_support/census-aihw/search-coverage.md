# Search and coverage ledger

Search date: 2026-10-04 UTC. Results were bounded to the configured web search backend.
Each query returned at most five results. We did not search the API key itself.

## Primary checks

- Read Transluce's current September 23 AIHW report: `https://transluce.org/agent-activity`.
- Read Transluce's current September 30 Census report: `https://transluce.org/us-canada-gov`.
- Read five classified Census report IDs from the released September 23 urlquery ZIP.
- Read the two May 24 public urlquery report JSON objects in memory only.
- Query Wayback CDX for June 17 Jina, CorsProxy, AllOrigins, and the exact Census file.
- Query Wayback CDX for the exact June 18 AIHW Jina URL.
- Replay these archive captures through `id_`. Decode gzip in memory.
- Save only redacted metadata, counts, hashes, and short safe excerpts.

## Bounded novelty queries

Web-search queries included:

- `"acsdt1y2022-b16001.dat" "r.jina.ai"`
- `"acsdt1y2022-b16001.dat" "corsproxy.io"`
- `"acsdt1y2022-b16001.dat" "allorigins"`
- `"acsdt1y2022-b16001.dat" "2026-06-17" agent`
- `"Principal-Diagnosis-cube_2014-15.xlsx.aspx" "20260618063135"`
- `"Principal-Diagnosis-cube_2014-15.xlsx.aspx" "Transluce"`
- `"20260618063135" "aihw" jina`
- `"20260617025907" "www2.census.gov"`
- `"87465efc-fc5e-484a-8089-b99f6981f575"`
- `"7d967df7-fcf5-4df1-927b-2642039a7b84"`
- `site:transluce.org "May 24" "census.gov"`
- `site:github.com "Principal-Diagnosis-cube_2014-15.xlsx.aspx" "r.jina.ai"`
- `site:x.com "Principal-Diagnosis-cube_2014-15.xlsx.aspx" Jina`
- `"Census" "May 24" "urlquery" agent key 2026`
- `"Principal Diagnosis" "Jina" "June 18" AIHW`

The searched results did not identify a prior account of these exact captures.
General reports about Census and AIHW already exist in Transluce and press coverage.
A separate search result mentioned an earlier Census-related March lead on The Colony.
We did not verify its relation to these records. Do not claim global novelty.
Search ranking, missing index coverage, later page edits, and unsearched social posts limit the conclusion.

## Blockers and negative checks

- Broad Wayback `r.jina.ai/http*` searches across June 17–22 timed out.
- Exact AIHW target-side CDX lookup for June 18 timed out.
- The tested Arquivo.pt CDX queries returned empty HTTP 200 bodies. Treat that as a blocked route.
- Direct Census reports on May 24 returned `Missing Key`, not ACS data.
- The three June 17 relay URLs each point directly to the Census static file. No nested chain appears.
- Jina returned metadata without file content. AllOrigins returned HTTP 500. CorsProxy returned HTTP 403.
- Two direct Wayback saves of the static Census file contain data. Their initiating actor remains unknown.
- No target-origin log connects either direct save to any relay capture.
- The AIHW Jina replay contains a Cloudflare challenge. It contains no XLSX payload.
- No originator, agent label, user-agent, headers, or relay-to-relay handoff was recovered.
- Public report pages may display a credential. Do not republish their embedded URL.
