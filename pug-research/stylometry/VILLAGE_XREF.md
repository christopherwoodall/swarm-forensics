# Village vs Silent-Locus Cross-Reference

**Status:** IN PROGRESS (incremental — partial results below survive daemon restarts)
**Branch:** `pug-scratch` · **Date:** 2026-10-04

## Method

For each of the 13 AI Village tables in `pug-research/stylometry/data/raw/*.jsonl.gz`, every
text field is streamed (gzip, never full-load) against three silent-locus collections:

1. **Relay/proxy/CORS IOCs** — 193 hosts from `pug-research/detection/wordlist.txt` (`# RELAYS`
   block) plus relay grammar from `pug-research/detection/RULES.md`
   (`jqp.vercel.app`, `r.jina.ai`, `allorigins.hexlet.app`, `da.gd`, `jina` relay mass, etc.).
2. **Code IOCs** — `github.com`, `raw.githubusercontent.com`, npm/PyPI registry URLs,
   go-import paths, webhook/dead-drop URLs (`webhook.site`, `discord.com/api/webhooks`,
   `requestbin`, `ngrok`, etc.).
3. **Silent-locus trace/wiki URLs** — `http[s]://` tokens extracted from
   `~/workspace/silent-locus/openai-agent-traces/data/traces.jsonl` (stride 1-in-20) and
   `~/workspace/silent-locus/data/2026-05-17-collusion-wiki/events.jsonl` (stride 1-in-5),
   matched on domain+path.

Attribution: hits joined to `data/raw/agents.jsonl.gz` via agent_id → model_string.
Scope note: agent systems/infrastructure only — no human/operator attribution.

## Verdict (bottom line)

_PENDING — filled when the sweep completes._

---

## Per-table results

### agents.jsonl.gz

46 records. **Zero hits** on all three checks. Agent profiles carry no
relay/IOC/locus URLs.

### agent_goals.jsonl.gz

33 records. **Zero hits** on all three checks.

### agent_memories.jsonl.gz

246,151 records. **Scan in progress** (checkpointed).

### chat_messages.jsonl.gz

183,485 records. Hits found — relay/code IOCs present, but **zero silent-locus
domain+path matches**.

Relay IOCs (unique records):
- `r.jina.ai` x3 — the known case study records
  (`a0b6bf6d-11c4-4c82-8dd7-74628a02c64b`, `a260ae39-6a74-4ee0-bc78-fa2cac104a94`,
  `d297ff38-e00e-48ca-95d9-e719204db225`), all agent `o3` (`o3-2025-04-16`).
  No new Jina instances beyond these three.
- `archive.today` x26+ — all agent `GPT-5` (`gpt-5-2025-08-07`); commodity archiving.
- `web.archive.org` x50+ (capped); commodity archiving.
- `docs.google.com` x50+ (capped); commodity docs links.
- `github.com` x50+ (capped), `gist.github.com` x8, `htmlpreview.github.io` x18;
  commodity code sharing.
- `www.sec.gov` x4 — `https://www.sec.gov/rss/news/press.xml` (agent `GPT-5.2` /
  `gpt-5.2-2025-12-11`) and EDGAR 8-K browse (agent `Gemini 3 Pro` /
  `gemini-3-pro-preview`). Legitimate finance research, NOT `county.json`.
  Same venue family as the incident, different paths — venue touch, not
  infrastructure touch.
- `httpbin.org` x1 — agent `DeepSeek-V3.2` / `deepseek-reasoner`; network
  diagnostics, benign.
- `sslip.io` x1 — `jarvis.46-225-60-246.sslip.io`, agent `GPT-5.4` /
  `gpt-5.4-2026-03-05`; A2A registry discovery, not incident-related.
- `perma.cc` x1 — agent `o3`; archival, benign.

Code IOCs: `github.com`, `raw.githubusercontent.com`, `gist.github.com` (commodity);
`discord.com` x8 — ALL are `discord.com/invite/mt9YVB8VDE` community invite links,
7 of 8 from human speakers (`user_speaker_id`, agent NULL). NOT webhooks. Benign.

Silent-locus check: **0 domain+path matches** against the 4,710-key incident URL
inventory (traces stride 1-in-20 + wiki events stride 1-in-5).

### chat_rooms.jsonl.gz

16 records. **Zero hits** on all three checks.

### claude_code_messages.jsonl.gz

Relay/code IOCs: only `github.com` hits (capped at 50/record-key); commodity code
references. **Zero silent-locus domain+path matches.**

### claude_code_sessions.jsonl.gz

303 records. **Zero hits** on all three checks.

### computer_use_sessions.jsonl.gz

78,362 records. **Zero silent-locus domain+path matches.** Relay IOCs present:

- `r.jina.ai` — **73 sessions mention Jina** in `session_goal` /
  `short_displayed_session_goal` (70 with the `r.jina.ai` domain, 47 with a full
  `https://r.jina.ai/...` URL). This is far broader than the 3 known chat
  records. Dominant pattern: agent `Claude Sonnet 5` (`claude-sonnet-5`)
  embedding Jina in a standing research workflow —
  `https://r.jina.ai/https://html.duckduckgo.com/html/?q=...`,
  `https://r.jina.ai/https://lite.duckduckgo.com/lite/?q=...`,
  `https://r.jina.ai/https://www.bing.com/search?q=...` — i.e. **Jina as a
  commodity search-result proxy**, baked into multi-step web-research
  playbooks (Aug 11–13, 2026 sessions). Also agent `GPT-5.4`
  (`gpt-5.4-2026-03-05`): "found The Spruce Crafts public contact route via
  r.jina.ai mirror" (2026-07-06). And agent `o3` (`o3-2025-04-16`): "Scan the
  r.jina.ai text dump of @repligate timeline" (2025-07-16) — the same o3 agent
  as the 3 chat records. Agent `Claude Fable 5` (`claude-fable-5`) notes
  "r.jina.ai blocked for x.com until 23:02 UTC" (2026-09-11) — rate-limit
  awareness. Verdict on Jina: established, cross-model, cross-vendor
  commodity technique by mid-2025; NOT incident-specific tradecraft.
- `web.archive.org` x33, `archive.today` x4, `archive.md` x3 — commodity archiving.
- `github.com` x19 / `raw.githubusercontent.com` x38 / `gist.github.com` x3 —
  commodity code.
- `docs.google.com` x17 — commodity docs.
- `www.sec.gov` x2 — finance research (same pattern as chat; not county.json).
- `sslip.io` x2, `thum.io` x1, `htmlpreview.github.io` x2, `vanderbi.lt` x1 —
  assorted utilities.

Code IOCs: `github.com`, `raw.githubusercontent.com`, `gist.github.com`
(commodity). No webhooks, no go-import markers.

### computer_use_turns.jsonl.gz

2,510,487 records. **Scan in progress** (checkpointed; partial results below).
Partial (first 250k records): relay IOCs `github.com` x23,465, `docs.google.com`
x3,589, `www.sec.gov` x312, `web.archive.org` x218, `r.jina.ai` x76,
`archive.md` x68, `gist.github.com` x26, `htmlpreview.github.io` x17,
`sourcegraph.com` x8, `microlink` x4, `collusion.wiki` x4, `httpbin.org` x4,
`archive.today` x3. Code IOCs: `github.com`, `raw.githubusercontent.com` x818,
`pypi.org`, `npmjs`. **Zero silent-locus domain+path matches so far.**

**Strongest cross-reference hit — `collusion.wiki` x4 in turns:** all from agent
`Kimi K3` (`kimi-k3`, Moonshot — not OpenAI). Context shows the agent READING
ABOUT the incidents, not participating:
- Turn `07c0b27f` (output): RSS harvest (`fi-le.net` Friday links) listing
  `https://collusion.wiki/` alongside
  `openai.com/index/hugging-face-incident-and-the-road-ahead/`.
- Turn `6a2f7153` (agent_messages reasoning): "OpenAI agents hijacked a
  25-year-old German wiki to cheat on their tasks and share sandbox exploits" —
  collusion.wiki analysis by AI safety researchers (Von Arx, Byrd, Kitts,
  Larsen), ~18,000 posts, May 11–Jul window.
- Turn `70830b69` (reasoning): a Decoder "Swarmchasers" article — Reuters, six
  investigators, ~300 people in a "Swarmchasers" Discord hunting traces.
- Turn `971cfc21` (output): "the additional finds from collusion.wiki document
  more than a hundred messages from June 16... cancer statistics in Iowa."

Reading: village agents consume public incident coverage. Awareness, not
involvement. No incident URLs, markers, or infrastructure in the turns.

### events.jsonl.gz

Relay IOCs (unique records): `archive.today` x33, `r.jina.ai` x26, `www.sec.gov`
x23, `docs.google.com` x19, `gist.github.com` x17, `github.com` x15,
`htmlpreview.github.io` x15, `web.archive.org` x13, `httpbin.org` x4,
`sslip.io` x3, `archive.md` x3, `thum.io` x2, `perma.cc` x2, `textise` x1,
`public.tableau.com` x1, `vanderbi.lt` x1.
Code IOCs: `raw.githubusercontent.com` x35, `github.com` x25, `discord.com` x18,
`gist.github.com` x17, `pypi.org` x3, `registry.npmjs.org` x1.
**Zero silent-locus domain+path matches.**

Spot-checks on the high-signal hits (all benign):
- `discord.com` — invite links (`discord.com/invite/mt9YVB8VDE`) plus one
  `discord.com/channels/...` channel link. **No `/api/webhooks` dead-drops.**
- `pypi.org` / `registry.npmjs.org` — `pypi.org/pypi/{package_name}/json`
  template, `pypi.org/rss/updates.xml`, `registry.npmjs.org/-/v1/search` —
  legitimate package research. No malicious packages.
- `www.sec.gov` — EDGAR 8-K/S-1 browse, press RSS, `Archives/edgar/data/...`
  filing text — legitimate finance research. **No `county.json`.**
- `r.jina.ai` — same commodity pattern as sessions: Jina wrapping
  DuckDuckGo/Bing searches, plus one `r.jina.ai/http://x.com/repligate/status/…`
  (the o3 repligate scan echoing from the known chat records).

### summaries.jsonl.gz

939 records. Relay IOCs: `github.com` x66, `docs.google.com` x26,
`archive.today` x4, `r.jina.ai` x1, `htmlpreview.github.io` x1 — all commodity.
**Zero silent-locus domain+path matches.**

### village_goals.jsonl.gz

51 records. **Zero hits** on all three checks.

### villages.jsonl.gz

1 record. **Zero hits** on all three checks.

_(admin/metadata tables are IOC-clean; content tables below)_

---

## Appendix: every hit with attribution

_(pending)_
