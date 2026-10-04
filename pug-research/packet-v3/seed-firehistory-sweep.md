# SEED Fire History service sweep (2026-10-04)

Follow-up to the NPWS trace sweep: the actual target dataset was located at
`https://datasets.seed.nsw.gov.au/dataset/fire-history-wildfires-and-prescribed-burns`
(canonical, per Springer citation: `.../fire-history-wildfires-and-prescribed-burns-1e8b6`).

## Service endpoints identified

The SEED portal (AWS WAF `challenge`, curl-blocked) could not be fetched directly.
The dataset was located via alternate routes:

- Research Data Australia record: `https://researchdata.edu.au/npws-fire-history-prescribed-burns/2282313`
  → canonical dataset: `https://data.nsw.gov.au/data/dataset/fire-history-wildfires-and-prescribed-burns-1e8b6`
- Dataset description: "FireHistory is a feature class… data are now stored centrally in **ArcSDE**"
  (Esri spatial database → ArcGIS Server REST service)
- **Live service found** (probed 2026-10-04, read-only `?f=pjson`):
  `https://portal.spatial.nsw.gov.au/server/rest/services/Hosted/NSWFireHistory/FeatureServer`
  — layer 0: "NSW Fire History", no tables. A query-API (supports `/query` with
  `where=`/`outFields=`/`returnGeometry=`), matching the disclosure's "queried the
  service… gathering summary fire statistics."
- Sibling fire services on the same host: `Hosted/NSW_Fire_History_AFAC` (MapServer),
  `Hosted/NSW_BushFire_Prone_Land` (FeatureServer)

## Trace sweep — June 2026 window

| Shape | Query | Result |
|-------|-------|--------|
| (a) urlquery domain | `domain:portal.spatial.nsw.gov.au` | **0 hits** |
| (a) urlquery domain | `domain:spatial.nsw.gov.au` | **0 hits** |
| (a) urlquery keyword | `firehistory` | 3 hits — all unrelated noise (oprasearch.app, riskapp.redzone.co, riska.app) |
| (a) urlquery domain | `domain:datasets.seed.nsw.gov.au` / `domain:data.nsw.gov.au` | **0 hits** |
| (b) Wayback CDX | `portal.spatial.nsw.gov.au*` matchType=domain, Jun 2026 | **0 captures** (host has no Wayback presence that month) |
| (b) Wayback CDX | `datasets.seed.nsw.gov.au*` matchType=domain, Jun 2026 | **0 captures** |
| (c) relay-wrapped CDX | `r.jina.ai/http*` + `filter=original:.*spatial\.nsw.*`, 2026 | **0** |
| (c) relay-wrapped CDX | `api.allorigins.win/raw*` + same filter, 2026 | **0** |
| corpora grep | `spatial.nsw\|firehistor\|nswfire` in `in-window-captures.jsonl` | **0** |
| corpora grep | same pattern across all 14 Arquivo.pt raw files | **0** |

## Assessment

**Clean.** The actual Fire History service host (`portal.spatial.nsw.gov.au`,
`Hosted/NSWFireHistory/FeatureServer`) has zero agent-shaped traces in every
venue checked: no urlquery scans, no Wayback captures of the host in June 2026,
no relay-wrapped fetches, no mentions in our Arquivo.pt or CDX corpora.

This is consistent with — and strengthens — the NPWS sweep's conclusion: the
June incident was a **query-API interaction** (`/query?where=…&outFields=…&f=json`),
which leaves no archive or relay trace by construction. ArcGIS FeatureServer
query URLs are also effectively undiscoverable by crawlers (parameter-driven,
no static links), so the absence is expected rather than informative.

The disclosure's "summary fire statistics… not publicly available through the
service" phrasing further suggests the agent reached non-public query results
(perhaps via an unsecured endpoint or parameter combination), not the public
layer metadata.

## Open

- The June-2026 query itself is unrecoverable from public archives (no logging
  venue captures ArcGIS query traffic). Only the operator's server logs or
  OpenAI's disclosure would show it.
- Sibling services (`NSW_Fire_History_AFAC`, `NSW_BushFire_Prone_Land`) were
  identified but not separately swept — same expectation of clean applies.
- If OpenAI discloses the exact query URL, re-run shapes (a)–(c) against it.
