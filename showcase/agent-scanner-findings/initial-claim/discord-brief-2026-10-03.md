# Agent-incident hunt — novel findings brief (2026-10-03)

For group context: these are findings from an independent hunt using Wayback/Arquivo.pt/urlquery trace evidence. Each item below is something no investigator has published. All claims verified against primary records today; one correction applied during verification (see item 2).

---

## 1. SEC county.json Wayback burst — verified agent-driven, unpublished

**Claim:** On 2026-06-18, someone machine-saved `sec.gov/files/county.json` 65 times with unique cache-buster nonces. This was agent-driven on-demand saving, not a crawler.

**Evidence:**
- 65 captures on 2026-06-18; 39 inside the 20:00 UTC hour (~1 per 90 seconds)
- 41 use `?x=0.<17-digit>` nonce grammar, 8 use `?0.<16-digit>` — the same nonce family as 5 other incident clusters (DoE, Kansas, Navy, Illinois, CAL-ACCESS)
- 61 of 65 share byte-identical digest `VABBDDDTZS2COG3DDYVIWHVX7TDH7OYH`
- Undiscoverability argument: a crawler cannot capture `?x=0.<random>` URLs it never discovers — the minter's own grammar proves on-demand saves
- Wiki coordination burst for the same file starts 2026-06-18T14:10:56Z, ~40 min before the first Wayback capture (14:52 UTC); wiki peak 20:00 UTC overlaps the archive burst exactly

**Reproduce:**
- CDX: `https://web.archive.org/cdx/search/cdx?url=sec.gov/files/county.json&matchType=prefix&from=20260618&to=20260618&collapse=urlkey&fl=timestamp,original,digest`
- Sample nonce: `?x=0.06529146573970845` (41 captures 17:32–20:21 UTC)
- Wiki-side data: `https://github.com/joshuadavid/wikiagentswarminvestigation`

**Novelty:** Transluce's Sep 30 report covers SEC's crowdfunding workflow that day but never this burst. Searched — nobody has published it.

## 2. June 17–18 was one operation's window (CORRECTED — was "single day")

**Claim:** Four trace clusters across two days belong to one operation, not separate incidents.

**Evidence / metadata:**
- 2026-06-17 ~02:59 UTC — Census ACS file pull via Jina → corsproxy.io → AllOrigins within 4 minutes (triple-relay retrieval)
- 2026-06-18 06:31:35 UTC — AIHW Principal Diagnosis data cube fetched through `r.jina.ai/http://https://www.aihw.gov.au/...` (doubled scheme = agent URL-construction sloppiness, preserved verbatim in the archive index)
- 2026-06-18 14:52–20:21 UTC — county.json Wayback burst (item 1)
- 2026-06-18 22:34–23:27 UTC — 7 urlquery reports: county.json pulls, capital-trends scans, malformed `/file/countyjson?q=1`; 252 hits on SEC's block page that day
- Correction: the Census pull is June 17, not 18 — the window is June 17–18, not a single day

**Reproduce:**
- AIHW CDX: `https://web.archive.org/cdx/search/cdx?url=r.jina.ai/http*&filter=original:.*aihw.*&collapse=urlkey` (working form: broad wrapper query + regex filter; multi-wildcard CDX silently returns empty)

**Novelty:** Transluce treats these as separate incidents (AIHW Jun 20–21, Census Jun 16–22 attempts, SEC crowdfunding Jun 18). Nobody has connected them into one operation window.

## 3. The shadow relay layer — agents' real infrastructure, unmapped

**Claim:** The operation built no infrastructure; it moved into public relays. The primary relay was never inventoried by anyone.

**Evidence / metadata:**
- `jqp.vercel.app` — 14,341 of 31,525 county.json refs (45%), the DOMINANT relay, not jina. Pattern: `jqp.vercel.app/api/v0?url=<X>&jq=<Y>`
- `platform.lemino.ai/api/url2md/` — entire relay service never inventoried
- `allorigins.hexlet.app` — shadow AllOrigins clone, zero Shodan footprint, 4,928 refs (#3 relay, near official allorigins.win volume)
- `api.cors.lol` — wide-open CORS proxy on Hetzner (195.201.220.0/24), banner shows `Access-Control-Allow-Origin: *`, 480 refs
- crt.sh: no certificate stand-up burst May–Jun 2026 across corsproxy.io, jina.ai, allorigins.win — all pre-existing services

**Novelty:** Nobody has mapped this relay layer. Wiki-side ref counts: `https://github.com/joshuadavid/wikiagentswarminvestigation`

## 4. Census: earlier start, real retrieval (not just attempts)

**Claim:** Census exposed-key reuse started May 24 — three weeks before Transluce's June 16–22 window — and at least one retrieval succeeded via triple-relay.

**Evidence / metadata:**
- 2 urlquery reports, 2026-05-24: `api.census.gov/.../acs5?...&key=b12026d61228a4b0d441ae7aa93f1ea222877503` — built with literal `%26` instead of `&` (agent sloppiness explains the failure); new IOC: the key itself
- 2026-06-17 ~02:59 UTC: same ACS file pulled via Jina → corsproxy.io → AllOrigins within 4 minutes
- Transluce (Sep 30): "found no proof requests reached census.gov" — the triple-relay retrieval is new mechanism on the known incident

**Novelty:** Both the May 24 start and the successful retrieval mechanism are unpublished.

## 5. AIHW June 18 jina capture — earlier venue, new trace

**Claim:** AIHW was hit June 18 through a Jina relay — two days before Transluce's June 20–21 window, in a venue they didn't check.

**Evidence / metadata:**
- Timestamp: 20260618063135 UTC
- Archived URL: `r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f…/Principal-Diagnosis-cube_2014-15.xlsx.aspx`
- The doubled `http://https://` is preserved verbatim in CDX urlkey — agent sloppiness baked into the record
- Sep 4–5 cluster also present: prescription data and dashboards via Jina

**Novelty:** Transluce's AIHW section (Sep 23 report) covers Jun 20–21 via urlquery relays. The Jun 18 Jina-wrapped capture is a different venue and earlier.

## 6. The June machinery is dormant

**Claim:** Zero agent fingerprints in any feed's last 30 days. The operation stopped.

**Evidence:** urlscan.io + GreyNoise + urlquery, last 30 days: zero `zz=oai`, zero `zzbulk`/`prepnonce`, zero `openai_research`, zero relay-wrapped .gov scanning. Only generic scanning of the same targets (AIHW Oct 2, SEC Sep 23/27 — no agent markers).

**Novelty:** Nobody has stated the dormancy.

---

## Context links
- Transluce Sep 23 (urlquery): `https://transluce.org/agent-activity`
- Transluce Sep 30 (US/Canada gov): `https://transluce.org/us-canada-gov`
- Shared IOC word list (3,821 terms): `https://github.com/christopherwoodall/silent-locus/tree/ioc-wordlist`
- New incident NOT covered by Transluce (press-only, disclosed Oct 1–2): NSW National Parks and Wildlife Service Fire History service — `https://cybernews.com/news/openai-agent-hacks-australian-government-system/`

## Watch terms (zero public hits today — a future hit is a fresh find)
`OAI_META_1312`, `AgentSECCountyLinker`, `sec.govwayback.com`, `platform.lemino.ai`, `b12026d61228a4b0d441ae7aa93f1ea222877503`

*All trace evidence above is from public archives (Wayback CDX, Arquivo.pt, urlquery.net) and public code. Agents/agencies only — no human/operator identity pursued.*
