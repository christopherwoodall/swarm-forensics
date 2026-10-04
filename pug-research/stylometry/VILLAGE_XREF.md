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

_(pending — largest table, streamed last)_

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

_(pending)_

### computer_use_turns.jsonl.gz

_(pending — largest table, streamed last)_

### events.jsonl.gz

_(pending)_

### summaries.jsonl.gz

_(pending)_

### village_goals.jsonl.gz

51 records. **Zero hits** on all three checks.

### villages.jsonl.gz

1 record. **Zero hits** on all three checks.

_(admin/metadata tables are IOC-clean; content tables below)_

---

## Appendix: every hit with attribution

_(pending)_
