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
| `r.jina.ai` | 0 | **195** | 0 | **3** (chat) |
| `da.gd` | 0 | 3 | 0 | 0 |
| `corsproxy.io` | 0 | 4 | 0 | 0 |
| `github.com` | 0 | 0 | 0 | dominant (all tables) |
| `civilrightsdata.ed.gov` | 12,542 (÷20) | 0 | 0 | 0 |

**`r.jina.ai` is the only URL chunk shared across layers.**
Everything else is segregated to exactly one layer.

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
