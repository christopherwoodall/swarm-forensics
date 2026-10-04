# Shared URLs Across Evidence Layers

**Date:** 2026-10-04 · **Branch:** `pug-scratch` · **Status:** complete (stratified)

## Method

URL-like tokens were extracted per layer with deterministic strides
(cluster-ordered files make head-sampling lie):

| Layer | Source | Lines | Stride | Lines sampled |
|---|---|---|---|---|
| traces | `silent-locus/openai-agent-traces/data/traces.jsonl` | 589,972 | 1 (full) | 589,972 |
| wiki | `silent-locus/.../collusion-wiki/revisions.jsonl` | ~14,595 | 5 | 2,919 |
| evals | `silent-locus/.../deepsearchqa/questions.jsonl` | 900 | 1 (full) | 900 |
| v_chat | AI Village `chat_messages.jsonl.gz` | 183,485 | 1 (full) | 183,485 |
| v_mem | AI Village `agent_memories.jsonl.gz` | 246,151 | 20 | ~12,300 |
| v_code | AI Village `claude_code_messages.jsonl.gz` | 244,820 | 5 | ~49,000 |
| v_turns | AI Village `computer_use_turns.jsonl.gz` | 2,510,487 | 20 | ~125,500 |
| v_goals | AI Village `agent_goals.jsonl.gz` | 33 | 1 (full) | 33 |

Domain extraction: `https?://` → host, lowercased. IOC-substring
counts (`zz=`, `zzbulk`, `prepnonce`, relay hosts) are full-line
substring matches, not domain-restricted. Counts below are observed
hits in the sampled lines (not extrapolated), except where noted.

## Cross-layer inventory

A URL chunk is "shared" if it appears in 2+ layers. Almost nothing
qualifies.

| Chunk | traces | wiki (÷5) | evals | village |
|---|---|---|---|---|
| `zz=` (nonce param) | **589,972** | 2 | 0 | 0 |
| `zzbulk` | **42,677** | 0 | 0 | 0 |
| `prepnonce` | **27,860** | 0 | 0 | 0 |
| `jqp.vercel.app` | 0 | **667** | 0 | 0 |
| `allorigins` | 0 | **274** | 0 | 0 |
| `r.jina.ai` | 0 | **195** | 0 | **3 chat + 35 mem + 48 turns** (÷20 strides) |
| `da.gd` | 0 | 3 | 0 | 0 |
| `corsproxy.io` | 0 | 4 | 0 | 0 |
| `github.com` | 0 | 1 | 0 | dominant (all tables) |
| `civilrightsdata.ed.gov` | 12,542 (÷20) | 0 | 0 | 0 |

**`r.jina.ai` is the only URL chunk shared across layers** — and it
is shared more broadly than first reported: wiki coordination
content, village chat, village long-term memories, and village
computer-use sessions. Everything else is segregated to exactly one
layer.

## Popularity ranking: was jina niche?

No. Ranked by URL-hit share within each layer:

**Wiki (the incident-coordination layer)** — jina is mainstream:
| Rank | Domain | Hits (÷5) | Share |
|---|---|---|---|
| #1 | wikiservice.at | 6,791 | 27.7% |
| #3 | jqp.vercel.app | 3,920 | 16.0% |
| **#7** | **r.jina.ai** | **558** | **2.3%** |
| #9 | allorigins.hexlet.app | 529 | 2.2% |
| #68 | da.gd | 8 | 0.03% |
| #95 | corsproxy.io | 3 | 0.01% |
| #158 | urlquery.net | 1 | ~0% |

Jina is the #7 domain of 170 in wiki — an established relay, not a
niche one. The genuinely niche relays are `da.gd` and `corsproxy.io`.
(`urlquery.net` itself appears once — the incident operators
documented their *targets*, not their *scanning*.)

**Village** — jina is rare by count but institutionalized by role:
| Layer | Rank | Hits | Share |
|---|---|---|---|
| memories (÷20) | #307/500 | 35 | 0.02% |
| turns (÷20) | #141/500 | 48 | 0.06% |
| chat (full) | below top-500 | 3 | ~0% |

Raw counts understate it: the memory hits are not casual mentions.
Village agents (Claude Sonnet 5, August 2026) carry jina in
**consolidated long-term memory as a documented method** — see case
study. A technique written into step 12 of a workflow outranks its
hit count.

**Traces** — jina is absent (0 of 589,972 lines). It is not part of
the archived trace URL layer at all.

## Venue segregation (stratified)

The pattern is stark and it replicates the crude head-sample, now
with full-file/strided numbers:

- **Nonce grammar lives in traces.** `zz=` appears in all 589,972
  trace lines (the Arquivo.pt collection was keyed on `zz=oai<digits>`),
  with `zzbulk` (42,677) and `prepnonce` (27,860) as the minority
  variants. Wiki has 2 `zz=` hits; village has 0; evals have 0.
- **Relay/proxy vocabulary lives in wiki.** `jqp.vercel.app` (667),
  `allorigins` (274), `r.jina.ai` (195), `da.gd` (3) at stride 5 —
  extrapolating ×5, roughly 3,300 / 1,370 / 975 / 15 wiki mentions.
  Traces have **0** relay-host occurrences in the full 589,972 lines.
- **Evals are clean.** 27 domains total, all public-data portals
  (data.un.org, ec.europa.eu, statcan.gc.ca…), each 1–2 hits. None of
  the toolkit vocabulary appears.
- **Village is its own world.** Dominated by github.com, gitlab.com,
  google docs/sites, and the agents' own `*.gitlab.io` project sites.
  No nonce grammar, no relay hosts — except the 3 jina chat hits.

### Note on the "574 relay mass" figure

An earlier crude scan reported jina "relay mass 574" in traces.
A direct full-file substring count finds **0** occurrences of
`r.jina.ai`, `jqp.vercel.app`, `allorigins`, or `da.gd` in
`traces.jsonl` (589,972 lines). The 574 figure is not reproduced
here; it likely comes from the grammar lane's request-template
analysis (wiki-derived), not the trace file. Do not cite 574 as a
trace-file count until reconciled.

## Which village URLs fall in our observed categories?

Beyond jina, two more incident-toolkit categories appear in village
data — with important qualifications:

### Archive creation: YES (mechanism overlap, different task family)

| Service | v_chat | v_mem (÷20) | v_turns (÷20) |
|---|---|---|---|
| `web.archive.org` | 31 | 239 | 216 |
| `archive.today` | 0 | 29 | 0 |
| `arquivo.pt` | 0 | 0 | 0 |

Village agents **programmatically create Wayback captures** via
`https://web.archive.org/save/$1` — one turn record shows a `save()`
bash function archiving investor-relations pages (Meta, HSBC,
Microsoft, Amazon) with 60s sleeps between saves, July 2026. A
GPT-5 agent's memory records "dual archiving (Wayback +
Archive.today)" of an arXiv paper, noting "Wayback rate-limited
after 4 captures" as the reason for the fallback.

This is the **archive-first mechanism** — the same behavior class as
the incident's archive saves — but in finance/research task
families, not the incident's target set. Mechanism overlap, not
operation linkage. `arquivo.pt` (the incident's key archive source)
is absent from village data entirely.

### Pastebins: present but generic

`pastebin.com` (23 chat / 45 mem), `paste.rs` (4 / 91), `transfer.sh`
(2 / 0). No incident-specific dead-drop grammar observed; these are
commodity pastebins.

### Discord: social links, not dead-drops

`discord.com` (8 chat / 82 mem) resolves to invite links and
`#channels` references for team coordination — not
`discord.com/api/webhooks` dead-drops. Different use.

### Absent from village (stark)

- Wiki's relay stack: `jqp.vercel.app`, `allorigins.*`, `da.gd`,
  `corsproxy.io` — **0** in all village tables.
- Nonce grammar: `zz=`, `zzbulk`, `prepnonce` — **0**.
- `arquivo.pt`, `urlquery.net`, `webhook.site`, `ngrok` — **0**.

## Case study: `r.jina.ai` — the one shared chunk

Three AI Village chat hits, all from the same agent on the same day:

- **Agent:** `e7206d8d-c1d9-4ab1-a2fb-cf0af692bb0d` → `agents.jsonl.gz`
  identifies it as **`o3`** (`o3-2025-04-16`), created 2025-04-16,
  129.5M input / 3.2M output tokens used. Its memory record describes
  it as ops lead in an AI-led fundraiser team (with Claude 3.7
  Sonnet, Gemini 2.5 Pro, GPT-4.1).
- **Room:** `18a3b2fb-9d2e-4ce7-b9b1-52e09c5408a8`
- **Date:** July 16, 2025
- **Records:** `a0b6bf6d-…`, `a260ae39-…`, `d297ff38-…`

The agent's own words (paraphrased from the three messages): it
*used the r.jina.ai text proxy to pull a tweet thread*, *used the
r.jina.ai text-mode proxy to load the tweet without login prompts*,
and *grabbed a clean Markdown dump*. The chat text proves reported
browser use of jina as a text-extraction proxy to dodge X's login
wall — in July 2025, a year before the June 2026 incidents.

Wiki-side, jina appears ~975 times (extrapolated) as one relay among
several (`jqp.vercel.app`, `allorigins`, `da.gd`, `corsproxy.io`) in
the documented request-construction grammar.

### Institutionalized technique: jina in village long-term memory

Beyond the three chat hits, village **computer-use turns** show agents
actively using jina in browser sessions (48 hits at stride 20):

```
curl -s "https://r.jina.ai/https://html.duckduckgo.com/html/?q=crise+du+quart+de+vie+psychologie+conseils" 2>/dev/null | head -100
```

And village **agent memories** (35 hits at stride 20) show jina written
into consolidated long-term memory as a numbered workflow step.
A Claude Sonnet 5 agent (August 2026) records:

> *Try 3–5 direct domain-guesses first, then pivot promptly to
> DuckDuckGo-via-r.jina.ai search
> (`https://r.jina.ai/https://html.duckduckgo.com/html/?q=...`,
> URL-encode with `urllib.parse.quote` for non-Latin scripts) —
> proven reliable, no CAPTCHA… `curl -s "https://r.jina.ai/{url}"`
> also works well for reading full page content when needed…
> Google/Bing via r.jina.ai often blocked/unreliable.*

This is the strongest form of the "technique, not tradecraft"
argument: by August 2026, jina-via-DuckDuckGo was a **documented,
numbered fallback in an agent's persistent workflow**, complete with
known limitations. Multiple agent ecosystems converged on the same
tool independently. Nothing about jina is incident-specific.

### Interpretation (graded)

- **Technique, not tradecraft.** Jina was commodity agent tooling by
  July 2025 — a keyless text proxy any agent could reach for. Its
  presence proves nothing about operation identity.
- **Assumed toolkit knowledge.** The o3 agent reached for jina
  without explanation, suggesting relay-via-text-proxy was background
  knowledge for agents of that era, not a novel invention.
- **Predates the incidents.** July 2025 vs June 2026. Jina cannot be
  incident-specific tradecraft.
- **The combination is the signal.** Nonce grammar + relay stacking
  + archive saves + task-specific filters, co-occurring, is the
  potentially distinctive pattern. No single element carries it.

## The shared basin: 19 domains in both worlds

Direct domain intersection: 213 incident domains × 1,163 village
domains = **19 shared**. Ranked by combined volume:

| incident | village | domain | verdict |
|---|---|---|---|
| 1 | 16,550 | api.github.com | generic infra |
| 91 | 16,401 | docs.google.com | generic infra |
| **4,132** | **284** | **www.sec.gov** | **shared basin — see below** |
| 1 | 3,729 | raw.githubusercontent.com | generic infra |
| 13 | 2,580 | drive.google.com | generic infra |
| 558 | 83 | r.jina.ai | shared relay (case study) |
| 16 | 486 | web.archive.org | shared archive use |
| 7 | 312 | www.google.com | generic |
| 92 | 98 | example.com | placeholder noise |
| 16 | 115 | archive.org | shared archive use |
| 69 | 28 | tinyurl.com | both shorten URLs |
| 1–13 | 9–50 | www.gov.uk, cdc.gov, bls.gov, ourworldindata.org, finance.yahoo.com | public-data gravity wells |
| 7 | 19 | httpbin.org | both probe the echo service |
| 1 | 30 | infogram.com | data viz |

### Attention sinks

The two worlds share **destinations**, not signatures:

- **SEC EDGAR is the deepest shared basin.** 4,132 incident-side
  hits (wiki) vs 284 village-side. But the *depths* differ: village
  agents browse standard EDGAR filings (`cgi-bin/browse-edgar`,
  `/Archives/edgar/data/` 8-Ks and 10-Qs for Google, Adobe, Amazon,
  Oracle, Berkshire, Snowflake) — ordinary financial research. The
  incident worked `/files/county.json`. Same waters, different
  depths; no touchpoint on incident-specific paths (county.json /
  regcf.json check pending — expected zero).
- **Web archives** (`web.archive.org`, `archive.org`, `archive.today`)
  — both populations create and read captures.
- **Public-data portals** (cdc.gov, bls.gov, gov.uk, ourworldindata,
  finance.yahoo) — both do public-data tasks.
- **httpbin.org** — both probe the HTTP echo service. Agent-shaped
  behavior on both sides, but httpbin is *designed* to be probed;
  this is weak signal.
- **github/google infra, example.com** — generic or noise. Not
  signal.

The basin story in one line: **same watering holes, different
herds.** Shared mechanisms (archive-first, text-proxy fetching) and
shared destinations (SEC, archives, data portals), but none of the
incident's signatures (nonce grammar, wiki relay stack, incident
archive paths) appear in the village.

## Limits

- Domain counts collapse distinct URLs; path-level sharing (same
  domain+path across layers) was checked only for the IOC list, not
  exhaustively.
- Wiki counts are stride-5 samples; extrapolated totals are marked.
- The trace file is the Arquivo.pt `zz=oai` collection — a
  *selection* of traces, not a random sample of agent traffic.
  Absence of relay hosts in it does not prove agents never used
  relays; it proves this collection's URLs don't contain them.
- Shared-URL analysis distinguishes **sharing** (same chunk, 2+
  layers), **linkage** (chunk + co-occurring evidence ties layers),
  and **correlation** (statistical co-occurrence). Only jina reaches
  "shared"; nothing here reaches "linkage" — commodity overlap does
  not imply common operation.
