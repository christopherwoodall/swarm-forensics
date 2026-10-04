# Trace pulls — village URL expansion hunt

Coordinated trace-expansion hunt: mine URLs from the AI Village tables, pull traces for them from public sources, stage for review. Branch `pug-scratch`, nothing committed.

## Mining (4 parallel miners, all village tables)

| Miner | Tables | Unique URLs |
|---|---|---|
| A (chat) | chat_messages, chat_rooms | 14,980 |
| B (memories) | agent_memories (stride 5), agents | 111,438 |
| C (computer-use) | computer_use_turns, computer_use_sessions | 232,936 |
| D (code) | claude_code_messages/sessions, agent_goals | 5,289 |
| **Total** | | **~364,643** |

Raw miner outputs: `/tmp/miner_{chat,memories,computeruse,code}.jsonl` (ephemeral). Each row: URL, table, count, record ids, agent ids, IOC n-gram matches, subword tokens (`tok_subword` from `pug-research/stylometry/build_lexdb.py`).

IOC-match quality was weak in chat/memories/code (generic n-grams: github.com, USDA, safety-research domains). Computer-use turns were the gold: real browser sessions with relay URLs, archive-save URLs, and the incident-cluster's exact relay+target combos.

## Pulls (time-boxed to incident window 2026-05-01 → 2026-06-30)

97 priority URLs (16 jina-wrapped, 31 archive-save targets, 50 `*.gitlab.io` village domains):

| Source | Hit rate |
|---|---|
| urlquery.net (`date:[2026-05-01 TO 2026-06-30]`) | 0/97 |
| Wayback CDX (`from=20260501&to=20260630`) | 5/97 (5.2%) |
| arquivo.pt (unbounded query, local timestamp filter) | 1/97 (1.0%) |

Full per-URL verdicts: [TIMEBOXED.md](TIMEBOXED.md). Raw hits: [timeboxed_hits.jsonl](timeboxed_hits.jsonl) (102 hits with provenance). Clean negatives recorded — all 50 village `*.gitlab.io` domains returned zero urlquery reports in-window.

## Key findings

1. **Direct touchpoint**: village computer-use turns contain `https://allorigins.hexlet.app/raw?url=https%3A//www.sec.gov/files/county.json` — the exact relay+target combination from the June 2026 incident cluster.
2. **Shared construction artifact**: village turns contain `https://r.jina.ai/http://https://liagriffith.com/` — the same doubled-scheme bug as the AIHW incident URL. Harness-family fingerprint.
3. **Archive-save behavior**: village agents issue `web.archive.org/save/` requests themselves (e.g. SEC EDGAR content); the village project page `ai-village-agents.github.io/the-anchorage/harbor.html` has a 2026-05-18 Wayback capture, possibly agent-driven.
4. **Jina is toolkit culture**: 288 jina mentions across village computer-use turns; the July 2025 o3 agent used "the r.jina.ai text proxy" casually to dodge X's login wall — a year before our incidents.
5. **Verdict**: mostly disjoint worlds with a thin archive-touchpoint layer. Village infrastructure is invisible in urlquery during the incident window; the shared relay stack, archive-save behavior, and URL-construction artifacts are the bridges.

## Caveats

- Memories mined at stride 5 (1.9G file); computer-use at full pass.
- CDX exact-URL only; 6 timeouts retried. arquivo.pt failed transiently on first pass, retried clean.
- Giant-domain urlquery queries sampled; exclusion rests on distinctive-entity keyword probes.
- Read-only throughout: no archive captures created, rate limits respected.
