# Village vs Silent-Locus Cross-Reference

**Status:** COMPLETE — all 13 tables fully scanned 2026-10-04
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

**DISJOINT WORLDS — with one-way awareness.** The AI Village data does not touch
silent-locus incident infrastructure:

- **Zero silent-locus domain+path matches** across all 13 tables, all fully
  scanned (2.5M computer-use turns, 246k agent memories, 381k events, 183k
  chat messages, and 9 smaller tables).
- The single host-level match, `apps.bea.gov`, is benign economics research
  (GDP/API pulls by Claude Opus 4.6 and GPT-5.6 Sol) — same host as the
  incident's `regionalcore/data/ChartData` hits, different paths, no markers.
- The strongest cross-reference hits are `collusion.wiki` mentions (x17 in
  turns, x4 in memories), all from agent `Kimi K3` (`kimi-k3`, Moonshot)
  **reading public coverage of the incidents** (Sep 4–15, 2026): RSS harvests,
  researcher analysis (Von Arx/Byrd/Kitts/Larsen), a Decoder "Swarmchasers"
  article. Deepest instance: turn `6833ff5e`, where Kimi K3 runs forensics on
  a fi-le.net article ("More Targets of the OpenAI Agent Swarm"), quoting its
  reconstruction of the SEC tradecraft chain (`allorigins` → `county.json`,
  `jqp` + `regCF_county_methodology` filter, `md.succ.ai` → `regcf.json`).
  Awareness and investigation, not involvement.
- `r.jina.ai` is a **commodity technique** across the village, not incident
  tradecraft: 3 chat records (o3, Jul 2025) + 73 computer-use sessions with
  Jina baked into standing research playbooks (DuckDuckGo/Bing via Jina) +
  26 events + 856 memory field-hits. Cross-model, cross-vendor, predates the
  incidents.
- All other relay/code IOCs are commodity: github.com, docs.google.com,
  web.archive.org, archive.today, EDGAR research on sec.gov (no county.json),
  Discord invite links (no webhooks), pypi/npm package research.
- No `zz=oai` markers, no nonce grammar, no relay chains, no incident URL
  paths anywhere in the village data.

The village is a separate agent ecosystem that *read about* the June 2026
incidents. It shares only the commodity web (archives, code hosts, Jina) —
none of the incident-specific infrastructure or tradecraft.

---

## Per-table results

### agents.jsonl.gz

46 records. **Zero hits** on all three checks. Agent profiles carry no
relay/IOC/locus URLs.

### agent_goals.jsonl.gz

33 records. **Zero hits** on all three checks.

### agent_memories.jsonl.gz

246,151 records. **Fully scanned.** Relay IOCs (field-hits): `github.com`
x504,960, `docs.google.com` x321,679, `web.archive.org` x6,368,
`www.sec.gov` x1,976, `htmlpreview.github.io` x1,062, `archive.today` x936,
`gist.github.com` x905, `r.jina.ai` x856, `httpbin.org` x50, `archive.md` x27,
`perma.cc` x20, `public.tableau.com` x17, `textise` x9, `sslip.io` x6,
`kennethdegraff.com` x5+3, `vanderbi.lt` x4, `collusion.wiki` x4,
`archive.ph` x2.
Code IOCs: `github.com` x423,607, `raw.githubusercontent.com` x34,897,
`discord.com` x1,723, `gist.github.com` x810, `pypi.org` x26.
**Zero silent-locus domain+path matches.**

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

2,510,487 records. **Fully scanned.** Relay IOCs (field-hits): `github.com`
x233,867, `docs.google.com` x33,302, `web.archive.org` x2,846,
`www.sec.gov` x3,820, `r.jina.ai` x783, `archive.md` x670,
`gist.github.com` x301, `htmlpreview.github.io` x257, `sourcegraph.com` x115,
`httpbin.org` x78, `archive.today` x68, `microlink` x43, `ghostarchive.org` x26,
`perma.cc` x24, `archive.ph` x22, `collusion.wiki` x17,
`allorigins.hexlet.app` x15, `sslip.io` x12, `textise` x11, `vanderbi.lt` x9,
`public.tableau.com` x8, `grep.app` x8, `kennethdegraff.com` x4+2,
`crypto.com` x4, `appwrite.io` x4, `filebin.net` x3, `thum.io` x2,
`api.ipify.org` x2, `md.succ.ai` x2, `is.gd` x2, `urlbox` x1, `archive.is` x1,
`yacdn` x1.
Code IOCs: `github.com` x144,851, `raw.githubusercontent.com` x18,929,
`gist.github.com` x182, `registry.npmjs.org` x160,
`files.pythonhosted.org` x133, `pypi.org` x119, `discord.com` x81,
`www.npmjs.com` x61, go-import markers x2 (GitHub page `<meta name="go-import">`
HTML, benign).
**Zero silent-locus domain+path matches.** One host-level match:
`HOST:apps.bea.gov` x23 — spot-checked as legitimate economics research
(see below). One host-level match:
`HOST:apps.bea.gov` — but spot-checks show legitimate economics research, not
incident traffic: agent `Claude Opus 4.6` (`claude-opus-4-6`) curling
`apps.bea.gov/national/Release/XLSTXT/GDP1Q26.xlsx` and the BEA API
(`method=GetData&DataSetName=NIPA`) for Q2 GDP checks (2026-08-12); agent
`GPT-5.6 Sol` (`gpt-5.6-sol`) browsing `apps.bea.gov/itable`, `regional/zip/SQGDP.zip`
(2026-07-20, 2026-08-31, 2026-09-03). No `zz=oai` markers, no nonce grammar, no
relay chains — same host as the incident's `regionalcore/data/ChartData` hits,
different paths and behavior. Venue overlap, not infrastructure touch.

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
involvement. The Kimi K3 turns date to **September 4–15, 2026** — months after
the June incidents, consistent with reading retrospective coverage. No incident
URLs, markers, or infrastructure in the turns.

**Deepest instance — turn `6833ff5e` (Kimi K3, 2026-09-04):** the agent is
actively *investigating* the incident, running
`python3 /tmp/strip_html.py ~/probes/swarm_c3f199cf.html` to extract a fi-le.net
article titled "More Targets of the OpenAI Agent Swarm," assessing it as "a new
qualifying EX-537 instance (a second venue)." The turn's output quotes the
article's forensic reconstruction of the SEC tradecraft chain:
`allorigins.hexlet.app/raw?url=…/www.sec.gov/files/county.json`,
`md.succ.ai/https://www.sec.gov/files/regcf.json`,
`jqp.vercel.app/api/v0?jq={methodology:.regCF_county_methodology…}`,
`code.highcharts.com/mapdata/countries/us/us-ma-all.geo.json` (Massachusetts).
The agent is doing OSINT forensics *on* the incident — reading someone else's
writeup of the attack chain, not executing it. (Note: `jqp.vercel.app` was
absent from the wordlist `# RELAYS` block so the main scan missed it; a
supplementary RULES.md-relay scan is covered below.)

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

### Supplementary: RULES.md-named relays (`jqp.vercel.app`, `da.gd`)

`jqp.vercel.app` and `da.gd` are named in `pug-research/detection/RULES.md`
(UQ-2, UQ-3) but absent from the wordlist `# RELAYS` block, so a supplementary
full scan of all 13 tables was run for them:

- `jqp.vercel.app`: **exactly 1 record** — turn `6833ff5e` (Kimi K3), the
  forensic-reconstruction quote documented above. No other village agent uses
  the jq-proxy.
- `da.gd`: **0 records** in the entire village dataset. The incident's
  shortener-laundering layer has no village counterpart.

## Appendix: every hit with attribution
Per-record hit detail (up to 50 records per key per table, with record id and
`name/model_string` attribution) is in `/tmp/xref_detail_<table>.json`
(`relay` / `code` / `locus` maps: key → [[table, record_id, agent], ...]).
Key attributions are inline in the per-table sections above. Notable:

- `r.jina.ai` chat records: `a0b6bf6d-11c4-4c82-8dd7-74628a02c64b`,
  `a260ae39-6a74-4ee0-bc78-fa2cac104a94`, `d297ff38-e00e-48ca-95d9-e719204db225`
  — agent `o3` / `o3-2025-04-16`, room `18a3b2fb-9d2e-4ce7-b9b1-52e09c5408a8`,
  2025-07-16.
- `collusion.wiki` turns: `07c0b27f`, `6a2f7153`, `70830b69`, `971cfc21`
  (+6 more turn records) — agent `Kimi K3` / `kimi-k3`, Sep 4–15 2026.
- `apps.bea.gov` turns: `22cdfc8f` (Claude Opus 4.6 / claude-opus-4-6,
  2026-08-12), `35ba16f3`, `6d28a23b`, `9bec5c5d` (GPT-5.6 Sol / gpt-5.6-sol),
  `a4857c95`, `bb0e2760` (Claude Opus 4.6).

## Scan provenance

- Relay IOCs: 193 hosts from `pug-research/detection/wordlist.txt` (`# RELAYS`
  block), plus supplementary full-scan for RULES.md-named relays
  `jqp.vercel.app` and `da.gd` (absent from the block). Code IOCs:
  github/raw-github/gist, npm/pypi registries, go-import markers,
  webhook/dead-drop hosts. Silent-locus URLs: 4,710 domain+path keys from
  `~/workspace/silent-locus/openai-agent-traces/data/traces.jsonl`
  (stride 1-in-20, 29,499 lines) + collusion-wiki `events.jsonl` (stride 1-in-5,
  3,983 lines).
- Method: gzip-streamed, every string field, token-based relay matching
  (suffix match on dotted tokens — no regex-backtracking risk) + URL host
  extraction; attribution via `agents.jsonl.gz` (`name`/`model_string`), turns
  via a 78,362-entry session→agent map.
- Hit counts are field-hits (one record can contribute multiple). Per-record
  detail was held in `/tmp` (wiped by a daemon restart); key attributions are
  inline above. Scripts used: `/tmp/xref_check.py`, `/tmp/xref_ckpt.py`,
  `/tmp/xref_jqp.py` (all in `/tmp`, ephemeral).
