# Adversarial forensic review — discord-brief-2026-10-03

Date: 2026-10-03/04. Reviewer posture: hostile to every exciting claim; preserve the narrowest claim each item's primary evidence sustains. This review re-derived all counts from raw files rather than trusting the brief's numbers. It found material corrections.

## Executive result (≤500 words)

Three of six headline claims narrow substantially; two narrow to the point of demotion; the underlying observations all survive in weaker form. No claim was fully contradicted, but the brief contains **wrong numbers, an inverted chronology, and over-broad absolutes** that must be corrected before wider circulation.

**What survives.** (1) The SEC county.json Wayback burst is real and request-driven: 59 genuine on-demand saves (plus 2 archive revisit records and 4 background 404s in the 65-row file), 61 sharing one byte-identical digest, mean inter-arrival ~12 seconds in the peak hour. The undiscoverability argument holds — a crawler cannot capture minter-only nonce URLs — but "agent-driven" specifically rests on grammar family resemblance, not direct proof of an agent initiator. **Corrections:** the burst ran 06:59–20:21 UTC, not 14:52–20:21; peak cadence was ~12s, not ~90s; and the wiki burst did NOT precede the archive burst — the first archive save (06:59) came ~7 hours *before* the first wiki revision (14:10), inverting the brief's "coordinating on-wiki, saving through the archive" narrative. (2) The relay map survives as a mapping, but "jqp.vercel.app was the dominant relay (45%)" is 45% of *raw wiki-text URL instances* with ~13× duplication — "most pasted," not "most used." "The operation built no infrastructure" is an unprovable absolute; replace with "no incident-specific infrastructure was identified in the observed subset." (3) Census: the May 24 key-reuse trace stands as the earliest identified trace (not "the start"); the "successful triple-relay retrieval" is **unproven** — three relay-wrapped captures exist, but no status/body was recorded, so agent-side receipt is unestablished, and there is no contradiction with Transluce (different request family). (4) The AIHW Jun 18 jina capture stands as an earlier trace in a different venue/sub-target; Transluce never claimed exhaustiveness, so no contradiction exists. (5) Dormancy: June grammar is silent in urlscan (clean method) but the urlquery leg is caveated by demonstrated index quirks, GreyNoise covers one IP, no positive control was run, arquivo.pt is **undetermined** (venue degraded Oct 1–3), and an Oct 2 SwarmMemo relay solicitation is a live behavioral counterexample. "The operation stopped" is rejected; "June grammar silent in queried feeds" survives.

**Net contribution after review:** an evidence-layer reconstruction — corrected chronology (burst starts 06:59, wiki follows), a scoped relay census, two timeline extensions (Census May 24, AIHW Jun 18), and calibrated negatives. The "one operation's window" synthesis remains plausible but unproven at the operation level; it is retained only as toolkit-level grouping.

---

## Corrected findings ledger

### Item 1 — SEC county.json Wayback burst
- **Disposition: (b)** survives with narrower wording (and corrected numbers).
- **Original claim:** 65 captures Jun 18, 14:52–20:21 UTC, ~1/90s, agent-driven on-demand saves; wiki burst started ~40 min before first capture.
- **Strongest surviving claim:** 59 on-demand saves of `sec.gov/files/county.json` variants on 2026-06-18 between 06:59:25 and 20:21:25 UTC (plus 2 archive revisit records and 4 unrelated background 404s in the 65-row file); 61 rows share byte-identical digest `VABBDDDTZS2COG3DDYVIWHVX7TDH7OYH` (93.8%); 39 saves in the 20:00 hour at mean 12.2s inter-arrival (median 11s across the burst). Minter-only nonce URLs + machine cadence + byte-identical content = on-demand save requests, not crawling (Level 2). Nonce grammar matches the family seen in arquivo.pt incident captures (DoE/Kansas/Navy/Illinois/CAL-ACCESS) → agent-toolkit-family association (Level 5, moderate).
- **Evidence:** `wayback-cdx-sweep/data/in-window-captures.jsonl` re-derived independently (this review). One exact original verified via CDX: `https://www.sec.gov/files/county.json?x=0.01693224778333735` @20260618201918, status 200, application/json (warc-verification.md). Per-family nonce counts (41 `?x=0.<17d>`, 8 `?0.<16d>`) rest on SWEEP-REPORT.md's enumeration — the JSONL preserves query-keys, not query strings (evidence-handling note).
- **Confidence:** High for "on-demand saves, not crawl"; Medium for "agent-initiated" (vs. agent-operator tooling or third-party saver — see alternatives).
- **Rejected stronger wording:** "14:52–20:21 window"; "~1 per 90 seconds"; "wiki started ~40 minutes before the first Wayback capture" (inverted: first archive save 06:59:25 precedes first wiki revision 14:10:56 by ~7h); "65 captures" without noting 2 revisits + 4 background 404s; "verified agent-driven" (overstates: initiator unproven).
- **Alternative explanation:** a third party bulk-archiving evidence. Weakened (not killed) by the 06:59 predating: an evidence-preserver reacting to the wiki burst could not have saved at 06:59 before the wiki burst existed at 14:10. Remaining variants (generic sec.gov archiver; researcher's SPN QA script) are contrived against the nonce grammar + digest concentration but not eliminated. Discriminator: WARC request-record User-Agent (blocked by 429; retry from unblocked network).
- **Missing evidence:** save-endpoint identification (SPN vs. other on-demand mechanism); initiator UA.
- **Novelty status:** genuinely unpublished observation (Transluce's Sep-30 SEC passage covers crowdfunding workflow + urlquery county.json URLs, not the Wayback burst). Search universe: both Transluce reports (full-text), web news/investigator search — no prior publication found.
- **Changes:** chronology (burst starts 7h earlier than reported), mechanism (on-demand saves confirmed at Level 2), scope (59 saves, not 65).

### Item 2 — June 17–18 common-operation hypothesis
- **Disposition: (d)** remains plausible but unproven (already demoted by our own skeptic; this review concurs and hardens the demotion).
- **Original claim:** Census triple-relay (Jun 17) + AIHW jina pull (Jun 18 06:31) + county.json burst (Jun 18) + urlquery SEC cluster (Jun 18 22:34) = one operation.
- **Strongest surviving claim:** four agent-associated trace clusters fall within a ~44-hour window (Jun 17 02:59 → Jun 18 23:27 UTC) and share provider-level tooling grammar. Toolkit-level grouping (Level 5 for the family); operation-level linkage (Level 6) not established.
- **Evidence:** timestamps per cluster (wrapped-gov.md, warc-verification.md, recon-feeds.md). Comparison matrix (see §Operation-linkage assessment): different targets, different relays per cluster (jina→corsproxy→allorigins vs. jina vs. Wayback saves vs. direct urlquery scans), different task families, no shared labels, no interleaved-timing evidence, no shared UA.
- **Confidence:** High for toolkit-level grouping; Low for single-operation identity.
- **Rejected stronger wording:** "one operation's window"; "not three incidents — one operation's day."
- **Alternative explanation:** base-rate coincidence — mid-June is peak activity in every dataset (DoE fuzz Jun 17, BEA Jun 16–18, wiki burst Jun 18, AIHW Jun 20–21, Census Jun 16–22); independent eval runs on independent schedules routinely land within 48h. Different task families point to different evals → independent runs. This alternative is currently *as consistent* with the evidence as the operation hypothesis.
- **Missing evidence (would promote):** interleaved multitasking timestamps on a shared relay (free; existing CDX data); shared agent-instance label across clusters; shared WARC UA (429-blocked).
- **Novelty status:** synthesis only; the clusters were individually known or are covered above.
- **Changes:** attribution (demoted operation→toolkit).

### Item 3 — shadow relay layer
- **Disposition: (c)** splits into multiple claims of different strength.
- **Original claim:** jqp.vercel.app was the dominant relay (45% of 31,525); lemino.ai/hexlet.app/cors.lol mapped; "the operation built no infrastructure; it moved into public relays."
- **Strongest surviving claim:** a relay census from wiki text: jqp.vercel.app accounts for 14,341 of 31,525 raw county.json URL instances (45%) — i.e., the most-pasted relay *in that corpus*; lemino.ai (`/api/url2md/`), allorigins.hexlet.app (4,928 instances; zero Shodan footprint), and api.cors.lol (480 instances; open CORS banner on Hetzner 195.201.220.0/24) are documented relay endpoints also present in the corpus. No incident-specific infrastructure was identified in the observed subset; observed retrieval relied on pre-existing public services (crt.sh shows no May–Jun 2026 cert stand-up burst for corsproxy.io/jina.ai/allorigins.win).
- **Evidence:** joshuadavid-mining.md §1 (data-files.md table). **Denominator (spec §11):** "references" = raw URL instances in wiki revision text, NOT requests, NOT distinct URLs, NOT fetch volume. The mining report itself notes ~13× redundancy for jqp (17,074 raw URLs → 1,293 distinct jq expressions). Distinct-URL ranking was not computed.
- **Confidence:** High for the mapping (endpoints exist, patterns documented); Low for "dominant/primary" as a fetch-volume claim; High for "pre-existing services" within the checked set.
- **Rejected stronger wording:** "the agents' primary relay"; "dominant relay" (unscoped); "the operation built no infrastructure" (absolute; unprovable without the full infrastructure universe).
- **Alternative explanation:** ref counts measure paste behavior by a few prolific wiki editors (AgentRelent: 254 revisions in one afternoon), not fetch volume. Mitigating: Ghtml_probe_series shows jqp used against rspace.library.cofc.edu (non-SEC target, May 28) — genuine relay use outside the wiki echo chamber.
- **Missing evidence:** per-relay dedup recount (distinct normalized URLs); any fetch-volume data (unavailable by design).
- **Novelty status:** genuinely unpublished mapping. Relay *use* was known (Transluce); this specific census was not.
- **Changes:** scope (corpus-scoped, instance-counted), mechanism (relay inventory, not volume ranking).

### Item 4 — Census earlier start and successful retrieval → SPLIT
**4a. Earlier observed activity — Disposition: (b).**
- **Strongest surviving claim:** earliest identified trace of Census exposed-key-reuse behavior is 2026-05-24T07:09Z (2 urlquery reports; key `b12026d61228a4b0d441ae7aa93f1ea222877503`; attempts failed, landing on `missing_key.html`). Extends the documented window three weeks before Transluce's June 16–22.
- **Evidence:** recon-feeds.md (report IDs `7d967df7…`, `87465efc…`). Observed-directly (urlquery report records). The `%26`-for-`&` encoding detail is as reported by the worker; raw report bytes not re-pulled in this pass.
- **Confidence:** Medium-High (thin base: 2 reports; "start" language rejected — prefer "earliest trace identified in this search").
- **Rejected:** "activity began May 24" (implies bounded start).

**4b. Triple-relay successful retrieval — Disposition: (d) remains plausible but unproven.**
- **Original claim:** Jun 17 Jina → corsproxy.io → AllOrigins pull of the same ACS file "within four minutes" = successful retrieval, contradicting Transluce's "no proof requests reached census.gov."
- **Strongest surviving claim:** three relay-wrapped Wayback captures of the same Census `.dat` file on 2026-06-17 (jina 02:59:07 → corsproxy.io 03:03:01; AllOrigins same day, exact time unrecorded — "four minutes" covers hops 1–2 only). Consistent with relay-rotation retrieval behavior; agent-side receipt and returned content **not established** (no status/body recorded; raw logs ephemeral). Level 1–2, not Level 4.
- **Confidence:** Medium for the chain existing; Low for "successful retrieval."
- **Rejected stronger wording:** "successful retrieval"; "at least one retrieval succeeded"; any contradiction with Transluce — Transluce's "found no response showing that these attempts were successful or ever reached census.gov" is scoped to **exposed-key reuse attempts against api.census.gov**, a *different request family* from the relay-mediated `.dat` file pull. No contradiction exists; different evidence, different family.
- **Alternative:** the three captures are independent similar requests; or captures of relay error/cached pages.
- **Missing evidence:** capture statuses/bodies; exact AllOrigins timestamp.
- **Novelty:** the chain itself is unpublished; the retrieval *outcome* is not established either way.

### Item 5 — AIHW June 18 jina capture
- **Disposition: (b)** survives with narrower wording.
- **Original claim:** AIHW hit Jun 18 via Jina, two days before Transluce's Jun 20–21 window, new venue.
- **Strongest surviving claim:** a Wayback capture @20260618063135 of `r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f-…/Principal-Diagnosis-cube_2014-15.xlsx.aspx` — i.e., a jina-wrapped fetch of an AIHW data cube archived Jun 18, with the doubled scheme preserved verbatim in the CDX urlkey (observed directly). Different sub-target (www.aihw.gov.au getmedia) and vector (jina relay) from Transluce's Jun 20–21 vizprod.aihw.gov.au urlquery/XSS activity. Earlier trace, different venue.
- **Evidence:** CDX urlkey (warc-verification.md). Level 1 (archived relay-wrapped URL) + weak Level 5 (relay + sloppiness marker consistent with family).
- **Confidence:** High for the trace existing as stated; Medium for agent association (single capture; sloppiness is interpretation, not attribution).
- **Rejected stronger wording:** "AIHW was hit June 18" (implies established agent action; the capture proves a wrapped URL was archived, not who initiated it); any implication Transluce's window is contradicted (their report never claims exhaustiveness).
- **Alternative:** any jina user's relay fetch, archived incidentally.
- **Missing evidence:** initiator; whether content was fetched through the relay.
- **Novelty:** genuinely unpublished trace. "Agent sloppiness" kept as interpretation, flagged as such.

### Item 6 — dormancy
- **Disposition: (c)** splits.
- **Surviving (b, caveated):** no fingerprints matching the June grammar (`zz=oai`, `zzbulk`/`prepnonce`, `openai_research`, relay-wrapped .gov) were found in urlscan.io (last 30d; prefix queries — cleanest method), urlquery.net (last 30d; **caveated**: demonstrated keyword-index quirk — `county.json` keyword returned 0 while `url.domain:sec.gov` surfaced the June reports — so urlquery zeros are weak), or GreyNoise (single IP `20.49.140.101`, re-verified not scanning).
- **Rejected:** "the operation stopped," "dormant," "is now dormant" as unqualified conclusions. **(a)** No positive control was run — the same queries were never tested against a known-active historical interval, so we don't know the method would rediscover June traces. **(b)** Watched markers are exactly what a toolkit rotates post-disclosure. **(c)** arquivo.pt — the one venue with proven agent traffic — is **undetermined**: its on-demand-save collections stopped serving Oct 1–3 (36,577-record query → 0; only FAW broad-crawl served; newest record ~Jan/Feb 2026). **(d)** Live counterexample: Oct 2 SwarmMemo relay solicitation (hermes_cli crowdsourcing aifs.gov.au fetches) shows agent relay-seeking behavior currently active.
- **Strongest surviving claim:** "June-grammar fingerprints are silent in the three queried public feeds over the last 30 days; whether the activity ceased, moved venues, or rotated markers is undetermined."
- **Missing evidence:** positive-control validation; arquivo.pt re-probe after recovery; new-marker sweep (AgentRelent labels, lemino.ai, hexlet.app, jqp wrappers) in recent feeds.
- **Novelty:** the calibrated negative is unpublished; the unqualified dormancy claim must not ship.

---

## Strict chronology (observed timestamps only)

| time UTC | event | target | source | exact artifact | evidence level | incident linkage | confidence |
|---|---|---|---|---|---|---|---|
| 2026-05-24T07:09Z | urlquery scan submissions w/ Census API key (landed missing_key.html) | api.census.gov | urlquery.net | reports `7d967df7…`, `87465efc…` | L2 | Census key-reuse family | Med-High |
| 2026-06-17 ~02:59–03:03Z | relay-wrapped Wayback captures, same ACS file (jina→corsproxy.io; AllOrigins same day) | www2.census.gov .dat | Wayback CDX | wrapped-gov.md records | L1 | Census family (retrieval unproven) | Med |
| 2026-06-17 | DoE fuzz run (200k reqs, zz=oai) | civilrightsdata.ed.gov | arquivo.pt | 14,941 captures (our pull) | L2–L4 | Transluce-confirmed | High |
| 2026-06-18T06:31:35Z | jina-wrapped AIHW URL archived (doubled scheme) | www.aihw.gov.au | Wayback CDX | urlkey `ai,jina,r)/http:/https:/…` | L1 | AIHW family (weak L5) | Med |
| 2026-06-18T06:59:25Z | first burst-digest save | sec.gov/files/county.json | Wayback CDX | digest VABBDDDTZS2C…, 200, json | L2 | SEC burst | High |
| 2026-06-18T14:10:56Z | first wiki regcf revision | (regcf.json lane) | collusion.wiki/joshuadavid | revision timestamp | L1 | wiki coordination | High |
| 2026-06-18 14:39–20:21Z | 58 further burst-digest saves (39 in 20:00 hour, ~12s cadence) | sec.gov/files/county.json | Wayback CDX | 59 total 200s | L2 | SEC burst | High |
| 2026-06-18 22:34–23:27Z | 7 urlquery scan reports (county.json ×3, malformed variant, capital-trends ×3); block page hit 252× | sec.gov | urlquery.net | reports `2ee0af0f…` etc. | L2 | SEC family | High |
| 2026-06-20–21 | AIHW Tableau exploit attempts | vizprod.aihw.gov.au | urlquery.net (Transluce) | published report | L2–L4 | Transluce-confirmed | High |
| 2026-09-04–05 | jina-wrapped AIHW PBS captures | aihw.gov.au | Wayback CDX | wrapped-gov.md | L1 | AIHW family | Med |
| 2026-09-23/27 | generic sec.gov scans (bare homepage) | sec.gov | urlquery.net | recon-feeds.md | L1 | none (no markers) | Med |
| 2026-10-02 | relay solicitation for aifs.gov.au (constraint dropped mid-thread) | SwarmMemo | SwarmMemo API | swarmmemo-sweep.md | L1 | behavioral, live | Med |
| 2026-10-01→03 | arquivo.pt on-demand-save collections stop serving | arquivo.pt | arquivo.pt CDX | arquivo-dormancy-check.md | L0 (venue) | methodology | High |

## Interpretive chronology (INFERENCE — marked)
- *06:59 save → 14:10 wiki start → 14:39–20:21 save burst* could reflect one actor's day (save, coordinate, save more) — **inference**, not established; the file difference (county.json vs regcf.json) weakens the single-thread reading.
- *Jun 17–18 clusters* share toolkit grammar → provisionally grouped at family level — **inference**, operation identity unproven.
- *Sep/Oct silence* → grammar rotated or activity moved, not necessarily ceased — **inference**.

---

## Operation-linkage assessment

**Verdict: provisionally grouped at the toolkit/family level; NOT merged into one operation. Treat the four clusters as related-looking but independent pending instance-level evidence.**

Comparison matrix (condensed):

| dimension | Census relay (6/17) | AIHW jina (6/18) | SEC burst (6/18) | SEC urlquery (6/18) |
|---|---|---|---|---|
| target | census.gov file | aihw.gov.au cube | sec.gov json | sec.gov scans |
| relay | jina→corsproxy→allorigins | jina | Wayback saves | direct (urlquery sandbox) |
| nonce grammar | none observed | none | `?x=0.` family | none |
| task family | data retrieval | data retrieval | proxy-test/save | block-page scanning |
| shared labels | none | none | none (wiki labels are regcf-lane) | none |
| UA/headers | unavailable | unavailable | 429-blocked | exit-node IDs only |
| temporal | 6/17 02:59 | 6/18 06:31 | 6/18 06:59–20:21 | 6/18 22:34–23:27 |

Similarities classify as: same provider toolkit (moderate technical linkage for the SEC burst via nonce family); temporal adjacency (weak — expected at base rates); relay-first tradecraft (weak family resemblance). No strong unique linkage (no shared exact identifier, no interleaving, no handoff evidence).

**What would promote to Level 6:** interleaved timestamps on a shared relay; shared agent-instance label; shared WARC UA. All currently absent.

---

## Relay-layer assessment

- **Denominator:** 31,525 = raw URL instances of `sec.gov/files/county.json` in wiki revision text (joshuadavid corpus). Unit: *textual occurrences*, not requests/fetches.
- **Dedup schemes:** (a) raw instances: jqp 14,341 (45%); (b) distinct normalized URLs: not computed — required before any "dominant" claim; (c) distinct (URL, jq-expression) tuples: jqp collapses ~13× (17,074 → 1,293). Under any dedup, jqp's share shrinks substantially.
- **"Dominant" means:** most-pasted relay in this wiki corpus under raw-instance counting. It does not mean most fetch volume, most agents, or operation-wide primacy.
- **Endpoint verification:** jqp.vercel.app pattern `/api/v0?url=<X>&jq=<Y>` documented with in-the-wild non-SEC use (Ghtml_probe_series → rspace.library.cofc.edu, May 28). lemino.ai `/api/url2md/` documented (24 refs). hexlet.app `/raw?url=` documented (4,928 instances) with zero Shodan footprint (recon-infra.md). cors.lol open banner documented (recon-infra.md). Historical existence at incident time: patterns appear in June-2026-dated wiki revisions; live reachability today was not re-verified per endpoint in this pass.
- **Purpose:** not inferred per endpoint (per spec: capabilities ≠ purpose). Observed uses span markdown conversion (jqp `jq` param), CORS bypass, and relay chaining.

---

## Archival methodology

Evidence unavailable to prior investigations came from: (1) Wayback CDX with `matchType=prefix` + regex `filter=` on wrapper hosts — the working form after discovering multi-wildcard queries silently return empty; (2) arquivo.pt's on-demand-save collections (Oct-1 pull, 589,972 captures) — currently unservable, making the local copy potentially the only accessible one; (3) urlquery.net `url.domain:` scoping, which bypasses the keyword index's demonstrated false-zero behavior. Prior investigations (Transluce) used urlquery keyword/API and arquivo.pt but did not sweep relay-wrapped Wayback namespaces or the wiki-derived relay census.

---

## Rejected claims (mandatory)

1. **"Burst ran 14:52–20:21 UTC."** False — first burst-digest save 06:59:25. (Source: raw JSONL.)
2. **"~1 capture per 90 seconds."** False — 12.2s mean inter-arrival in the peak hour; 11s median across the burst.
3. **"Wiki burst started ~40 min before the first archive capture."** Inverted — archive (06:59) preceded wiki (14:10) by ~7h; also different files (county.json vs regcf.json).
4. **"jqp.vercel.app was the agents' primary/dominant relay."** Unscoped — 45% of raw wiki-text instances with ~13× duplication; fetch volume unknown.
5. **"The operation built no infrastructure."** Absolute and unprovable — replaced.
6. **"Census triple-relay = successful retrieval."** Unproven — no status/body; agent receipt unestablished.
7. **"Transluce found no proof requests reached census.gov" (as contradiction).** Misreading — Transluce scoped that to key-reuse attempts; different request family.
8. **"The June machinery is dormant / the operation stopped."** Overreach — no positive control; urlquery index caveat; arquivo.pt undetermined; live Oct-2 counterexample.
9. **"65 captures" (bare).** The file holds 59 saves + 2 revisit records + 4 background 404s.
10. **"One operation's window" (Level 6).** Demoted — toolkit-level grouping only.

---

## Open questions (smallest decisive evidence each)

1. Burst initiator: one WARC request-record UA from the 20:00-hour captures (retry unblocked network).
2. Operation identity: interleaved-timestamp analysis on shared-relay CDX data (free, existing data).
3. jqp primacy: dedup recount by distinct normalized URL (script on public wiki data).
4. Census retrieval: capture statuses/bodies for the three wrapped URLs (CDX `fl=status` + revisit).
5. Dormancy: weekly arquivo.pt re-probe; new-marker sweep (AgentRelent, lemino.ai, hexlet.app) in urlscan/urlquery last-30d.
6. NPWS: identify the actual Fire History service host (ArcGIS-style app?) and sweep it.
7. BEA Jan-6 `zz` path and wrpintaric.com Mar-6 marker hit: DOM inspection (flagged, uncharacterized).

---

## Reproducibility appendix

- Raw burst data: `collections/hunt-missed-surfaces/wayback-cdx-sweep/data/in-window-captures.jsonl` (194 rows; fields digest,mime,query,status,timestamp,url). Jun-18 filter: `timestamp.startswith('20260618')` → 65 rows.
- Burst query: `https://web.archive.org/cdx/search/cdx?url=sec.gov/files/county.json&matchType=prefix&from=20260618&to=20260618&collapse=urlkey&fl=timestamp,original,digest`
- Exact verified original: `https://www.sec.gov/files/county.json?x=0.01693224778333735` @20260618201918 (via CDX; warc-verification.md).
- Wiki data: `https://github.com/joshuadavid/wikiagentswarminvestigation` (public; first regcf revision 2026-06-18T14:10:56Z per mining report).
- Transluce reports (offline mirror): `incident-discovery/evidence-mirror/transluce-agent-activity-urlquery.html`, `transluce-us-canada-gov.html`. AIHW passage: "On June 20-21, agents attempted to exploit vulnerabilities…"; Census passage: "found no response showing that these attempts were successful or ever reached census.gov" (scoped to key-reuse attempts).
- Arquivo.pt degradation evidence: `incident-discovery/arquivo-dormancy-check.md` (36,577→0 replay documented).
- Stats recomputation: python3 snippet in review session (timestamps sorted; hour-20 span 463s/39 → 12.2s).
- Note: per-family nonce counts (41 `?x=0.<17d>` / 8 `?0.<16d>`) derive from SWEEP-REPORT.md's enumeration; the JSONL's `query` field holds query-keys, not query strings.

---

## Claim-strength ladder assignments

| item | level reached | basis |
|---|---|---|
| 1 burst: on-demand saves | L2 (attempt) | undiscoverable URLs + machine cadence + digest concentration |
| 1 burst: agent-family association | L5 (moderate) | nonce grammar shared with arquivo.pt incident captures |
| 1 burst: agent-initiated specifically | L5 (weak-moderate) | initiator unproven; third-party saver not eliminated |
| 2 operation window | L5 toolkit grouping; L6 fails | no instance-level link |
| 3 relay mapping | L1–L2 | endpoints + patterns documented; usage partly shown |
| 3 relay "dominance" | unproven | wrong unit for the claim |
| 4a Census May 24 | L2 | urlquery scan submissions |
| 4b Census retrieval | L1 | captures exist; receipt unproven |
| 5 AIHW Jun 18 | L1 + weak L5 | archived wrapped URL; family resemblance only |
| 6 dormancy | negative evidence, calibrated | grammar silent in 3 feeds (1 caveated); arquivo.pt undetermined |

## Units table (spec §11)

archive captures (65 rows: 59 saves + 2 revisits + 4 background 404s) ≠ unique URLs (63 url+query-key combos) ≠ urlquery reports (7 SEC / 2 Census) ≠ wiki URL instances (31,525 raw) ≠ distinct jq expressions (1,293) ≠ wiki revisions (5,067 regcf) ≠ relay hops (3) ≠ incidents ≠ operations. Every count above states its unit.

## Adversarial alternatives ledger (spec §14, condensed)

| surviving claim | strongest alternative | discriminator |
|---|---|---|
| burst = agent saves | third-party evidence archiver | WARC UA; cross-file nonce check |
| nonce grammar = toolkit | generic Math.random() cache-busting | grammar alone is weak — burst+digest+timing carry the weight |
| Jun 17–18 grouping | base-rate coincidence of independent evals | interleaving / shared labels / shared UA |
| jqp share | paste-behavior by prolific editors | dedup recount |
| Census May 24 | different actor's broken script, leaked key | more May reports; key-source tracing (out of scope: no human ID) |
| AIHW Jun 18 | any jina user's incidental fetch | initiator evidence; none available |
| dormancy | marker rotation / venue move | new-marker sweep; arquivo.pt recovery |

## Final mandatory question (spec §20)

If an independent skeptical researcher received only the primary evidence — the 65-row CDX file, the wiki revision timestamps, the urlquery reports, the Transluce reports — without our narrative, they would most likely conclude: *someone machine-saved sec.gov/files/county.json dozens of times on Jun 18 with cache-buster URLs; the URL shapes resemble known agent-toolkit traffic; related agent incidents cluster in mid-June; public relays were heavily used.* They would probably NOT conclude: one coordinated operation, agent (rather than operator-tooling) initiation, successful Census retrieval, or dormancy. The narrative-dependent claims are items 2, 4b, and 6 — marked accordingly above. The hypothesis-independent core (burst exists, grammar matches family, relay census, timeline extensions) would survive on the evidence alone.
