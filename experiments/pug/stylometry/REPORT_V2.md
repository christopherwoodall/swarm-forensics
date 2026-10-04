# Stylometry Report v2: functionally-matched cross-corpus comparison

Diagonal pairs match by text type and communicative function. Every run
logged to `runs_log.jsonl`. Baselines in `baselines.json`.

## Diagonal pairs

| # | Our side | Village side | Function |
|---|---|---|---|
| D1 | ours_wiki (14,591 revision bodies) | vil_chat_agent (173,493 agent chat msgs) | agent-to-agent coordination prose |
| D2 | ours_evals (900 questions) | vil_goals (33 goals) | task/goal statements |
| D3 | ours_gems_names (617 dirnames) | vil_code (244,820 claude_code msgs, assistant only) | code |
| D4 | ours_traces (29,498 URL records) | vil_computer_lex (2.5M turns' text) | behavioral traces |

Contamination/robustness pairs:
- C1: ours_wiki vs vil_chat_all (user rows included — tests contamination)
- C2: ours_traces_clean vs vil_computer_lex (analyst-note-free traces)

Reference: vil_memories (village-only long-horizon agent voice).

## Lexical results (7 methods per diagonal)

[PENDING — v2 build in progress]

## Contamination check (C1)

[PENDING]

## Action-sequence structure (D4 structural)

Computer-use turns (78,114 sessions, 2,510,487 turns) vs our trace records
(589,972 events). Lexical comparison treats behavior as text; this treats
behavior as behavior.

Computer side action distribution: `shell` 39.0% (979k — command
executions), `left_click` 14.7%, `scroll` 6.8%, `type` 6.4%,
`get_pixel_coords_of_element` 6.0%, `send_message_back_to_chat` 4.0%.
Characteristic loops: shell→shell (819k), left_click→left_click,
get_pixel_coords_of_element→left_click (locate-then-click),
type→key:Return, shell→send_message_back_to_chat→shell (execute-report loop).
Self-loop rate 0.493, mean run 1.91, max run 111, transition entropy 2.18 bits.

Trace side: 34 event types (incident:mime). Self-loop rate 0.971, mean run
34.5, max run 34,547, entropy 0.154 bits.

Honest reading: the trace-side numbers are dominated by collection order —
captures were pulled incident-by-incident, so long same-type runs are a pull
artifact as much as a behavior trace. The two sequences are NOT directly
comparable (per-session action order vs global timestamp order). The genuine
harness-level finding is computer-side: shell-dominated action mix, the
locate→click loop, the execute→report loop, and bounded stuck loops (max run
111 within sessions). Our side's stuck-loop evidence remains the hunt's
burst analysis (59 saves/hour), not this sequence.

## Seven non-lexical style experiments

[PENDING — runs on v2 diagonals]

1. punctuation profiles — [PENDING]
2. capitalization ratio + digit density — [PENDING]
3. sentence-length distributions — [PENDING]
4. markdown-structure markers — [PENDING]
5. URL density + embedding style — [PENDING]
6. hedging vs assertive ratios — [PENDING]
7. type-token ratio — [PENDING]

## Which findings change under apples-to-apples matching

[PENDING]

## Caveats

- vil_goals has 33 records — thin for statistical comparison; treat D2 as
  exploratory.
- The computer_use_turns download was truncated at 2.0 GB on first fetch
  (gzip EOFError); resumed via HTTP 206 to 2.47 GB and verified with gzip -t.
- Trace-side action sequences inherit collection order; see caveat above.
