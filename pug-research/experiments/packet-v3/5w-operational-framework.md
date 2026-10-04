# 5W Operational Framework — detecting agent-shaped behavior

Not a story about what happened. A machine for noticing when it happens again.

---

## Who — agent system identification

**Operational question:** which agent system produced this trace?

**What we extract:** harness bookkeeping, not calling cards. `zz=oai<epoch>` tags, OAI-prefix run labels, relay-stack choices, skill-ladder behaviors (the Wayback `/save/` instruction). Three separable levels — provider (OpenAI) vs eval/task family vs agent instance — because conflating them is how attribution goes wrong.

**Detection primitives:** tag-grammar filters, relay fingerprints, parameter-shape matching (the confirmed eval link worked through `survey_Year_Key=9`-style parameters, never question text).

**From this hunt:** the nonce grammar is a provider-level marker; the Massachusetts-county jq filter is task-level; nothing yet reaches instance-level.

## What — agent-shaped behavior

**Operational question:** what behavior pattern marks machine agency, as distinct from human browsing or ordinary crawling?

**What we extract:** the behavior vocabulary —
- nonce-bearing URLs not discoverable by ordinary crawl-based enumeration
- machine cadence (39 saves/hour, ~12s peak inter-arrival)
- fuzz-shaped parameter sweeps (documented params → metacharacters → encodings)
- relay ladders (direct → Wayback → Jina → AllOrigins → shortener)
- construction artifacts (doubled schemes, literal `%26`, 4-layer laundering chains)
- digest concentration (61 of 65 byte-identical = re-saving, not discovering)

**Failure-morphology taxonomy** (how attempts fail in public):
- Census: relay-rotating / wrapper-failure / retrieval-unconfirmed
- AIHW: single-relay / target-blocked / content-not-retrieved

**Detection primitives:** burst analysis on archive captures, digest-concentration ratios, inter-arrival distributions, relay-chain reconstruction.

## When — occurrence monitoring

**Operational question:** when does it occur?

**What we extract:** eval-season clustering (May–June 2026 run windows), burst timestamps, dormancy signals. The June 17–18 window and the May 24 earliest trace are monitoring anchors, not just history.

**Detection primitives:** time-series anomaly detection on the fingerprint set; standing watch terms (`OAI_META_1312`, `AgentSECCountyLinker`, `sec.govwayback.com` — zero public hits today, a future hit is an instant alert); weekly re-probes of degraded venues (arquivo.pt).

**Known gap:** direct query-API incidents (NPWS Fire History) leave no archive/relay trace by construction — monitoring has a venue-shaped blind spot, and the framework must say so.

## Where — URL basins

**Operational question:** extracted from IOCs, evals, and traces — do models have a basin for certain URLs?

**The basin concept:** a basin of attraction in URL-space. Models don't browse uniformly; they gravitate toward predictable shapes — API endpoints with query parameters, data files (`.json`, `.dat`, `.xlsx.aspx`), faceted-search URLs, relay-wrapped targets, archive save endpoints. The basin is enumerable and watchable.

**What we extract:** target-type distributions (APIs ≫ HTML pages), relay-wrapper preferences, path grammars (`/api/`, `/files/`, `/data/`, `/ajax/`, `/search/`), the double-slash canonicalization family.

**Detection primitives:** the IOC word list *is* a basin map (3,821 terms). New captures falling into the basin get flagged; the basin itself gets re-enumerated as new relay/path grammars surface. The v4 staging (82 candidates) is the basin's growth edge.

## Why — pattern identification, taxonomy, SOC operations

**Operational question:** why does any of this matter to a working SOC?

**Outputs (filters/queries):**
1. **Filter set:** the IOC word list as SIEM-compatible indicators — nonce grammar, relay hosts, tag families, watch terms.
2. **Monitoring queries:** the reproducible CDX patterns (`matchType=prefix` + regex filter on wrappers), urlquery domain searches, Arquivo.pt sweeps — each documented with its venue quirks (multi-wildcard CDX silently empties; date-bounded arquivo.pt is a zero-trap).
3. **Taxonomy:** failure morphologies, the claim-strength ladder (L0 artifact → L6 operation linkage), the evidence-bearing vs interpretive split — so analysts grade findings instead of narrating them.
4. **Calibration discipline:** every negative finding states its venue limits; every "dormant" is scoped to queried feeds; the rejected-claims ledger is mandatory, not optional.

**The loop this enables:** basin enumeration → capture monitoring → behavior classification → taxonomy update → new watch terms → basin re-enumeration. Each incident makes the next one cheaper to see.

---

*Built from the June 2026 incident hunt. Agents, agencies, infrastructure, public archival evidence only.*
