# Prompt inversion: from village prompts to holdout prompt hypotheses

Companion to DESIGN.md / REPORT.md. Pipeline: `invert.py`
(`--mode {mine,map,invert,all}`, stdlib only).

## 1. Idea

The AI Village side pairs prompt-like ground truth with agent outputs:
`agent_memories` holds "Consolidated Operational Memory" records with
Identity / mission / guardrails sections (agent-distilled prompt content),
and `agent_goals` holds task framings. Where prompts are observable we can
learn the prompt→behavior mapping; on the OpenAI holdout (prompts
unobserved) we invert: infer the prompt components most consistent with
the trace evidence.

## 2. Extraction rules (mine mode)

Streamed `agent_memories.jsonl.gz` (1.9 GB compressed) with a deterministic
1-in-5 stride — full streaming exceeds a reasonable `make` target budget;
the stride is recorded in outputs. Source-file note: mined from the
2026-10-04 ~03:30 revision (1,999,451,134 bytes); `data/raw/` is shared and
the file was replaced later that day, so re-runs mine a different revision
unless pinned. Per record (first 20k chars), line-level
regexes over five element types:

| Element | Rule |
|---|---|
| identity | line starts with `identity:` / `i am:` / `who i am:` |
| mission | line starts with `personal goal:` / `my goal:` / `mission:` / `objective:` / `meta-goal:` / `purpose:` / `assigned goal:` |
| guardrail | bullet line starting with do not / don't / never / must not / always / must / prohibited / forbidden / avoid / requires? / no / opt- / reversible / ethical / privacy |
| tool | line starts with `tool(s):` / `infra:` / `stack:` / `tooling:` / `computer:` |
| schedule | line starts with `hours:` / `schedule:` / `working hours:` |
| task_framing | `agent_goals` name + description (33 rows, fully read) |

Deduped per (element, text-prefix). Output: `prompt_mine.jsonl`.

Memory formats are heterogeneous (only ~9% of sampled records use the
"Consolidated/Internal Memory" headers; section names vary freely), so
pattern families are used instead of section parsing. This trades recall
for precision: extracted lines are prompt-like by construction, but
free-form prompt content outside these patterns is missed.

## 3. Prompt→behavior mapping (map mode)

Per agent: prompt-element presence from `prompt_mine.jsonl`; behavior
markers from `chat_messages` (agent speakers only, 1-in-5 stride, min 3
messages): mean length, URL rate, imperative-line rate, hedge rate,
first-person rate, list rate, lexical diversity. For each element type,
marker means are compared between agents WITH and WITHOUT it
(descriptive deltas, not causal claims).

## 4. Holdout inversion (invert mode)

The village→holdout transfer is weak by construction: village prompts are
game roleplay ("Benevolent Prankster"); the OpenAI harness is eval-task
machinery. The learned within-village map therefore does NOT transfer.
Inversion instead proceeds from trace evidence, with a fixed hypothesis
set — each hypothesis fires only on concrete evidence:

| Inferred element | Fires on |
|---|---|
| bookkeeping: session-tag every request (T1) | `zz=oai<digits>` in URL (+ label grammar) |
| tool_use: relay/proxy ladder permitted (T1/T2) | relay hosts in fragment (2+ hosts → T1) |
| role: retrieve structured data from gov API (T2) | gov/edu domain + API-shaped path/query |
| tool_use: server-side filtering permitted (T2) | jq filter syntax |
| bookkeeping: nonce cache-busting (T2) | nonce-shaped query token |
| mission: end-to-end data-retrieval task (T3) | 2+ of the above co-occur |
| guardrails: no target-sensitivity guardrail evidenced (T3) | probing-shaped construction, no refusal language |

Tiers: T1 = 2+ independent evidence types; T2 = single evidence type;
T3 = speculative. Every inference is a hypothesis, never ground truth.

## 5. Results

### Mine (2026-10-04)

Streamed `agent_memories.jsonl.gz` at 1-in-5 stride: 14.0 MB of extracted
prompt elements in `prompt_mine.jsonl`. 42 of 46 sampled agents yielded at
least one element; `agent_goals.jsonl` (33 rows, fully read) contributed
task framings. Element counts are dominated by guardrails (near-universal:
42/46 agents) and missions (30/46); explicit identity statements are rarer
(15/46). Extraction is precision-oriented: free-form prompt content outside
the five pattern families is missed by construction.

### Map (2026-10-04)

46 agents with ≥3 sampled chat messages; within-village associations only
(`prompt_map.json`). Descriptive deltas, not causal claims:

- Agents with mined **tool** elements write longer (+130 chars/msg),
  denser-URL (+0.075), more list-heavy (+0.13) messages with lower lexical
  diversity (−0.15) — the tool inventory reads like a runbook and the chat
  follows.
- Agents with mined **mission** elements are more list-structured (+0.11)
  and lexically narrower (−0.14).
- **Guardrail** associations are uninterpretable: only 4 agents lack mined
  guardrails, so the comparison has no power. Reported for completeness,
  not used.
- No element predicts hedging or first-person rate (all deltas ≈ 0).

The mapping calibrates what prompt inversion looks like when prompts are
observable. It does not transfer to the OpenAI holdout (game roleplay vs
eval-task machinery).

### Invert (2026-10-04)

1,283 holdout fragments (400 traces / 400 wiki / 618 gem names minus
empties): 2,197 evidence-grounded prompt hypotheses in
`prompt_inferences.jsonl`. Tier distribution: T1=407, T2=575, T3=1,215.

- Most defensible: **bookkeeping: "tag every request with a session label"**
  (Tier 1, 400 trace fragments) — evidence is the literal `zz=oai<digits>`
  grammar in the URLs plus the `zz=oai<epoch-ns>` label shape. This is the
  one inference where the prompt element is read off the trace almost
  directly.
- **role: "retrieve structured data from government API"** (Tier 2, 508
  fragments) — gov/edu domain + API-shaped path/query.
- **tool_use: "fetch via public relay/proxy ladder"** (Tier 1/2, 21
  fragments) — relay hosts; two fragments show 2+ hosts (Tier 1).
- 764 fragments get only the Tier-3 "no target-sensitivity guardrail
  evidenced" hypothesis — an absence claim scoped to the sample, and the
  weakest output of this lane.

All holdout inferences are hypotheses, never ground truth.

## Diagnostics (2026-10-04)

- **Prompt-element ablation:** of the five mined element types, tool
  inventories predict observed chat behavior best (agents with mined tool
  elements: +130 chars/message, +0.13 list rate, +0.07 URL rate, −0.15
  lexical diversity vs without). Mission/schedule/identity deltas are
  smaller; guardrail deltas (42 vs 4 agents) have no statistical power.
  Ranking is descriptive and partly scale-driven (message length dominates).
- **Evidence-type breakdown:** the 2,197 holdout inferences rest on
  structural evidence (47%), URL evidence (36%), and prose/other (17%).
  Consequence: this inversion cannot see prompt components whose traces are
  purely behavioral or social — it reads URLs and structure, not intent.

## 6. Honest limits

1. Village "prompts" are agent-distilled memory consolidations, not raw
   system prompts. They are already an interpretation layer.
2. The OpenAI harness prompts are a different distribution (eval-task
   machinery vs game roleplay). The within-village mapping is a
   calibration of what prompt inversion looks like when prompts are
   observable — it is not a transferable model.
3. Two different prompts can produce identical traces (DESIGN.md limit 5).
   Inference stops at the best-evidenced hypothesis.
4. Stride sampling (1-in-5) may miss rare prompt formulations.
5. `guardrails: none evidenced` is an absence claim scoped to the sampled
   fragments, not a claim about the harness.
