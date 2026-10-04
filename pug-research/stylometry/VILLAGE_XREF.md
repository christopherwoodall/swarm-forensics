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

_(pending)_

### chat_rooms.jsonl.gz

16 records. **Zero hits** on all three checks.

### claude_code_messages.jsonl.gz

_(pending)_

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
