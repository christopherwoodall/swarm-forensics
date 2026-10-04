# Detection Rules — agent-shaped behavior (5W operationalization)

Derived from the June 2026 incident hunt. Scope: agents, agent systems,
infrastructure, public evidence. No human or operator attribution is
attempted or implied by any rule below. A hit means *agent-shaped
behavior was observed*; it does not identify who launched it.

How to read a rule: **Catches** (what fires it), **Why it works**
(trace evidence it rests on), **Blind spots** (what it cannot see).
Every blind spot is load-bearing — a rule without a stated blind
spot is a rule you will misread.

---

## 1. urlquery.net search strings

urlquery search syntax: `q` keyword-matches submitted URLs; `url.domain:`
scopes to the target domain; `tags:` filters report tags;
`date:[YYYY-MM-DD TO YYYY-MM-DD]` bounds the window. Hyphenated
probe-name fragments (e.g. `e898-start`) cut hex-substring noise — a
bare hex fragment matches random UUIDs, hashes, and base64.

### UQ-1 — Nonce-grammar sweep (provider-level marker)

```
q=zz%3Doai date:[2026-01-01 TO *]
```

- **Catches:** submitted URLs carrying the `zz=oai<digits>` tag grammar
  (T_ZZ_OAI: 747 occurrences in the trace corpus) and its bulk variant
  `zzbulk<digits>` (2,184 in traces).
- **Why it works:** the nonce grammar is the strongest provider-level
  marker in the corpus. `oai` appears 89,241× in traces and 814× in gem
  names but 0× in eval questions — it is harness bookkeeping, not task
  text (stylometry REPORT.md, Finding 3). The confirmed DoE eval link
  was recovered from a bare URL carrying this grammar.
- **Blind spots:** the jqp/IHME cluster (24 reports, May 27–Jun 18)
  carried **no** `zz=` markers at all — linkage there rested on relay
  choice and timing only. A marker-less agent is invisible to this
  rule. Also misses percent-encoded variants (`zz%3Doai`) unless the
  encoded form is queried separately.

### UQ-2 — jq-proxy extraction (task-level marker)

```
q=jqp.vercel.app date:[2026-01-01 TO *]
q=jq%3D%5B date:[2026-01-01 TO *]
```

- **Catches:** server-side `jq` extraction requests through public
  jq-proxy relays — the agent outsourcing fetching *and* filtering to
  public infrastructure. jqp is the top relay in the request-grammar
  graph (3,887 mass) and the most-pasted relay in the wiki corpus.
- **Why it works:** the June 18 17:13 UTC report showed
  `jqp.vercel.app/api/v0?url=https://allorigins.hexlet.app/raw?url=
  https%3A%2F%2Fwww.sec.gov%2Ffiles%2Fcounty.json&jq=[.regCF_county_2019[]
  |select(.code|startswith("us-ma-"))]` — a task-specific Massachusetts
  extraction filter inside the Wayback burst window (jqp-ihme-lead.md).
  The `jq=` param (3,806 in traces) plus `.code` (2,397) and
  `.regCF_county_2019` (987) jq-op shapes are task-revealing.
- **Blind spots:** catches the relay, not the task — most jqp hits are
  generic fetches. The `jq=` filter must be read per-report to separate
  task-shaped extraction from ordinary use. Relay choice alone is
  weak evidence; it needs the burst-window or filter co-signal.

### UQ-3 — Relay-chain laundering (multi-layer nesting)

```
q=allorigins.hexlet.app date:[2026-01-01 TO *]
q=da.gd url.domain:jqp.vercel.app
```

- **Catches:** multi-layer relay nesting: target → CORS relay →
  shortener → jq-proxy → shortener. Documented 4-layer chain:
  `www.sec.gov → allorigins.hexlet.app → da.gd/4qPkK →
  jqp.vercel.app+jq(Massachusetts filter) → da.gd/Di7Cu`.
- **Why it works:** top nesting chains in the request-grammar graph
  (e.g. `[jqp.vercel.app, www.sec.gov]` ×717,
  `[jqp.vercel.app, allorigins.hexlet.app]` ×551,
  `[allorigins.hexlet.app, www.sec.gov]` ×464). The May 27 IHME
  cluster showed dual submission — `da.gd/iar2` 302ing to the same
  jqp URL submitted in full form at the same seconds.
- **Blind spots:** shortener links (`da.gd/*`) are opaque until
  resolved; urlquery only shows the submitted form. Chains assembled
  across separate reports require timestamp correlation, which the
  search API does not do for you.

### UQ-4 — Data-API basin targets

```
q=vizhub.healthdata.org date:[2026-01-01 TO *]
q=api.datausa.io date:[2026-01-01 TO *]
url.domain:sec.gov q=county.json
```

- **Catches:** agent-shaped traffic against known basin targets:
  health-data APIs (IHME vizhub), statistical APIs (datausa), and
  the SEC `county.json`/`regcf.json` family.
- **Why it works:** the basin concept — models gravitate to API
  endpoints, data files, and faceted-search URLs rather than browsing
  uniformly. Observed: 3× anemia/config + 4× anemia aggregate queries
  (May 27, 12:46–14:11 UTC), `api.datausa.io` (1,905 host mass),
  `www.sec.gov:files/county.json` (2,077 pathseg mass).
- **Blind spots:** the basin is enumerative, not predictive — a new
  target family outside the known list is missed until the basin map
  (IOC word list) is re-enumerated. Direct query-API incidents leave
  no urlquery trace at all (see runbook §3).

### UQ-5 — Watch-term tripwires (novelty strings)

```
q=OAI_META_1312
q=AgentSECCountyLinker
q=sec.govwayback.com
```

- **Catches:** first public appearance of the hunt's most novel
  strings. All three are at zero public hits as of 2026-10-03.
- **Why it works:** recon-code.md verified these strings exist in
  public code ONLY as unrelated identifiers or not at all — their
  agent-toolkit grammar forms have zero public presence. A future hit
  is a high-novelty event by construction.
- **Blind spots:** tripwires only fire on exact strings. A renamed
  marker (new prefix, new label family) evades them silently. They
  detect reuse of *known* tradecraft, never novel tradecraft.

---

## 2. Wayback CDX sweep patterns

CDX API: `web.archive.org/cdx/search/cdx?url=<pattern>&
matchType=prefix&filter=<regex>&from=<YYYY>&to=<YYYY>&output=json`.
Venue quirks (from the 5W framework — violate these and the sweep
lies to you): **multi-wildcard patterns silently return empty**;
keep one wildcard per query. **Date-bounded arquivo.pt queries are a
zero-trap**; sweep arquivo.pt unbounded, then filter client-side.

### CDX-1 — Burst-window capture census

```
url=sec.gov/files/county.json&matchType=exact&from=20260618&to=20260618
  &filter=statuscode:200&collapse=digest
```

- **Catches:** machine-cadence save bursts: 59 on-demand saves /
  65 raw captures on June 18 06:59–20:21 UTC, 39 in the 20:00 hour,
  ~12s peak inter-arrival, 61/65 sharing digest
  `VABBDDDTZS2COG3DDYVIWHVX7TDH7OYH`.
- **Why it works:** digest concentration is the discriminator —
  61 byte-identical captures = re-saving, not discovering. Human or
  crawler traffic does not produce 12-second cadence with identical
  digests across an 8-hour window.
- **Blind spots:** `collapse=digest` hides the burst if you only
  count captures. Always pull the uncollapsed series first, then
  compute the concentration ratio. Revisits and background 404s
  (6 of the 65) pollute naive counts.

### CDX-2 — Relay-wrapper prefix sweep

```
url=r.jina.ai/http*&matchType=prefix&filter=urlkey:.*sec.gov.*&from=2026&to=2026
url=r.jina.ai/http*&matchType=prefix&filter=urlkey:.*ed.gov.*&from=2026&to=2026
```

- **Catches:** Jina-mediated retrieval attempts against government
  data targets. The AIHW case: wrapper HTTP 200, `text/plain`,
  1,500 bytes at capture `20260618063135`, target-blocked underneath
  (archive-visible, target-blocked retrieval attempt).
- **Why it works:** `r.jina.ai` has 574 relay mass in the trace
  corpus and 3,545 wiki mentions; it is the documented laundering
  relay for blocked targets. Wrapper-200/target-blocked is the
  failure morphology to look for.
- **Blind spots:** r.jina.ai keyless access died after June 2026 —
  absence of new captures is venue death, not dormancy. CDX only
  indexes what the wrapper fetched; CAPTCHA/403 bodies at the target
  are usually unrecoverable (archive mirrors rate-limit).

### CDX-3 — Nonce-grammar filter sweep

```
url=arquivo.pt/wayback/cdx*&matchType=prefix
  &filter=original:.*(zzbulk|prepnonce|wbdisable|arqcb).*
  &filter=original:.*fresh=x[0-9]{10}\.
```

- **Catches:** arquivo.pt captures carrying the agent fuzz grammar:
  `zzbulk<digits>`, `prepnonce`, `wbdisable`, `arqcb`, and the
  `?fresh=x<epoch>.<random>` cache-buster template.
- **Why it works:** recon-code.md verified these grammar forms have
  zero public-code presence — they are toolkit-shaped, not
  organic. 14,941 DoE captures carried `zz=oai<digits>` on
  arquivo.pt alone (June 17).
- **Blind spots:** arquivo.pt's CDX is the zero-trap venue — always
  query unbounded and filter locally. Grammar drift (new param
  names) evades fixed regexes; re-derive the filter from the
  request-grammar graph each sweep.

### CDX-4 — Save-endpoint monitoring (forward-looking)

```
url=web.archive.org/save/*&matchType=prefix&from=<thisweek>&to=<thisweek>
  &filter=urlkey:.*(gov|api).*
```

- **Catches:** new on-demand saves against government/API targets —
  the earliest observable moment of a future incident.
- **Why it works:** the hermes-lineage finding — agents are
  instructed to create Wayback captures via `/save/`. The save
  endpoint is where agent archiving behavior first becomes public.
- **Blind spots:** high noise — legitimate researchers and
  archivists use `/save/` constantly. This rule needs the
  co-signals (nonce grammar, burst cadence, basin targets) before
  it means anything. Never alert on save-endpoint hits alone.

---

## 3. SOC runbook

### What to alert on (in priority order)

1. **Watch-term hit** (UQ-5: `OAI_META_1312`, `AgentSECCountyLinker`,
   `sec.govwayback.com`). Zero-baseline strings — any hit is novel.
   Page immediately.
2. **Burst + digest concentration** (CDX-1 pattern on any target):
   >10 captures/hour with >80% digest concentration. This is the
   machine-cadence signature.
3. **Nonce grammar on a new target** (UQ-1 / CDX-3): `zz=oai<digits>`
   or `zzbulk` appearing against a domain not in the basin map.
   New-target expansion is the incident signal.
4. **jq-proxy extraction with a selective filter** (UQ-2): `jq=`
   containing `select(`, `startswith(`, or field projections against
   a data file. Read the filter — it names the task.
5. **4-layer relay chains** (UQ-3): shortener → relay → shortener
   nesting around one target. Laundering depth is effortful; depth
   ≥3 is never casual browsing.

### What it means (claim-strength ladder)

- **L1 artifact:** a single URL carries agent-shaped grammar. Means:
  *some agent system* touched public infrastructure. Nothing more.
- **L2 burst:** cadence + digest concentration. Means: automated,
  repeated retrieval — a running task, not a curious click.
- **L3 task:** a selective filter (`startswith("us-ma-")`) or param
  shape (`survey_Year_Key`) names the data being extracted. Means:
  the task family is now observable.
- **L4 toolkit:** relay-stack + nonce-grammar + construction
  artifacts (doubled schemes, literal `%26`) co-occur. Means:
  shared launcher/toolkit across incidents — provider-level linkage.
- **L5 operation:** same task + same window + same toolkit across
  venues. Means: one operation. This is the highest claim this
  framework supports.
- **Never:** operator identity. No rule here reaches a human.

### What to check next (per alert)

1. **Resolve the full chain.** Shorteners first (`da.gd/*` 302s),
   then relay nesting. Document every hop — the chain *is* the
   tradecraft.
2. **Pull the burst series uncollapsed.** Compute inter-arrival
   times and the digest-concentration ratio before concluding
   anything about cadence.
3. **Read the filter, not just the relay.** A `jq=` param or query
   string names the task; the relay only names the tool.
4. **Cross-venue check.** Same target + same window in urlquery,
   CDX, and arquivo.pt = L5 material. One venue = L1–L2.
5. **Check the rejected-claims ledger before escalating.** The
   May 27–Jun 2 IHME cluster is a *candidate target family*, not a
   confirmed incident — no eval match, no agent markers. Do not
   upgrade it on relay choice alone.
6. **State the venue limits in the ticket.** Direct query-API
   interactions (ArcGIS `/query?where=...`, e.g. the NSW Fire
   History service) leave **no** archive or relay trace by
   construction. A clean sweep of urlquery/CDX/arquivo.pt does
   not clear a target — it only clears those venues.

### Standing watches (weekly)

- Re-run UQ-5 tripwires and UQ-1 nonce sweep; any new-target hit
  escalates to the runbook.
- Re-probe degraded venues (arquivo.pt unbounded sweep, CDX-3
  filter re-derived from the current request-grammar graph).
- Re-enumerate the basin: new relay hosts, new path grammars, new
  param shapes feed back into UQ-2/UQ-4 and the IOC word list.
- Review the rejected-claims ledger: AIHW is a *retrieval attempt*
  (wrapper 200, target blocked), not an incident; wiki→archive
  causality is falsified (first save preceded the first wiki
  revision); the gems are an honest negative (no goal-taxonomy
  coverage). Do not let closed findings drift back open.

---

*Evidence anchors: 5w-operational-framework.md (Who/What/When/Where/Why
primitives, venue quirks, claim ladder); jqp-ihme-lead.md (4-layer
chain, MA jq filter, IHME cluster bounds, 24-report sweep);
stylometry REPORT.md (relay/proxy/archive term tables, oai/zz
provider-marker distribution, Findings 1–4); grammar-network
request_grammar.json (relay mass: jqp 3,887 / allorigins 1,093 /
jina 574; top nesting chains; T_ZZ_OAI 747, T_PCT26 1,168;
param mass: survey_Year_Key 12,279, jq 3,806, zz 3,484;
jqop: .code 2,397, .regCF_county_2019 987).*
