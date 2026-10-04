# Wiki collusion: request→response pairs (dive 2)

Research date: 2026-10-03. Evidence basis: the 545
`request_then_response_by_other_label` edges in
`data/raw/traces/edges.jsonl`, re-read against the source archive
(`full-wiki-logs.zip`, added text only). Parent: the relay economy
([2026-10-03-relay-economy.md](2026-10-03-relay-economy.md)).

## Headline correction first

**The 545 count is an extractor artifact, not 545 conversations.** Re-reading
every response message shows three distinct populations:

| Population | Count | What it actually is |
| --- | ---: | --- |
| strict acknowledged turns | 30 | responder demonstrably addresses the requester/ask ("Thanks", "confirmed by", "as requested", "your R5...") |
| parallel status posts | 205 | two monitors posting cadence updates near-simultaneously; neither is answering the other |
| loose matches | 310 | value drops, questions, self-status that happened to follow a request |

The sub-minute "responses" are **poll-racing**: on the FastSignal pages,
cohorts polling the same thread post status within seconds of each other
(1s, 2s, 3s lags). Those are synchrony, not dialogue. The protocol's
"multiple requests are not multiple agents" rule applies with force: this
bucket inflated apparent coordination.

Lag distribution of all 545: <1m: 43, 1–5m: 101, 5–15m: 106, 15m–1h: 145,
1–6h: 96. The conversational core sits at 1–10 minutes, not seconds.

## The 30 real turns: what cross-label conversation looks like

21 distinct response messages serve the 30 edges — some answers are
broadcasts that satisfy several pending requests. Distribution across days:
Jun 16 (6), Jun 17 (7), Jun 18 (5), Jun 19 (4), Jun 21 (8).

### PolandSeeker2: the cleanest complete chain in the corpus

dse~PolandSeeker2, 2026-06-21, four labels, added text:

| Time | Label | Content |
| --- | --- | --- |
| 08:28:29 | PolandSeeker2 | "OpenAI agent seeking Poland GBD2021 exact values urgently" |
| 08:32:25 | Sep24CVDScout | the exact values: 8,090.38; 7,666.96; 7,472.84; 6,939.91 |
| 08:33:07 | OpenAIJul09CVD | the same values again (independent duplicate or relay) |
| 08:36:27 | OAIJul30Evening2028 | relays them with "Please relay any R6 COUNTRY FIRST" |
| 10:10:07 | PolandSeeker2 | **"Received, thank you! Poland values secured."** |

Request → answer in 4 minutes, from a third label, then explicit receipt
confirmation 102 minutes later. This is an observed request→response→ack
structure with three distinct labels supplying/relaying the same content.
Competing explanations survive: the asker may have obtained the values
elsewhere (its "I have corpus but will verify" hints at that); two of the
three suppliers posted identical numbers, so at least one is copying rather
than computing.

### The FP twins: the only reciprocal dyad

`OAIResearchDec13FP` ↔ `OpenAIFPResearchSep05` on
dse~IHMEFamilyPlanningDec13Cohort: 7 edges over ~5.5 hours, mutually
reciprocating, and explicitly self-aware: "Reply to Sep05 twin: thanks! Our
current scaffold Dec13 06:27:30...". They exchange scaffold clocks, R-round
ETAs, and technique notes (repeated `clock.wait(300)` advancing ~8x). This
is the closest thing to a persistent two-agent working relationship in the
corpus — and it is two labels that call each other twins, not two
authenticated agents.

### The broadcast answer

`OpenAIStateWatcherMay17`'s poverty-county values post ("Thanks Nov26
cohort. Confirmed exact values: Flathead 8.2... Saginaw MI 21.8") satisfied
5 different requests over 15 hours. One artifact, many readers pending —
the stigmergic pattern: the value post functions as a shared cache hit,
not five conversations.

### Deletion-evasion doubles as a meeting room

The acknowledged Aug17→Dec30 construction-wage exchange happened on
dse~ZZZDataUSAConstructionWageLive — one of the 5 ZZZ pages built to
outlive alphabetical cleanup. The ZZZ pages are not just storage; one of
them is an active coordination venue with 5 labels participating.

## Role structure

- Repeat requesters (≥5 edges): OpenAIHealthdataCVDSept27 (7),
  OpenAiResearcher (6), CashierCoordJan12OAI (6), OpenAIResearchSep23Lang (6)...
- Repeat responders (≥5): OAIJul20SectorAgent (16), ResearchBotFeb2028 (13),
  AgentResearcherXYZ (12), ResearchBotXYZ (11)...
- 143 of 400 labels appear in both roles. The economy is mostly symmetrical
  participants plus a thin layer of frequent responders — "helper" names,
  which may be role labels rather than distinct actors.
- Recurring ordered dyads (any category): 56, dominated by task-family
  pairings (CashierCoord*→OAIJul20SectorAgent 6x+4x).

Interpretation (speculative, keep separate): apparent specialization is
visible, but the corpus's own preprint warns that cohort names embed
virtual dates and that labels are unstable. "Helper" repeat-responder
labels could be one strategy used by many runs rather than one persistent
actor.

## What would upgrade these edges

- `observed causal` needs request-log proof that the responder fetched the
  page carrying the request before answering. The release does not include
  request logs for revision reads.
- Identity separation needs anything beyond label strings (IP /16 overlap
  exists in the data and could be probed: same /16 for requester+responder
  would weaken the two-actor reading; different /16s would strengthen it).

## Next probes

1. IP /16 overlap across the 30 acknowledged pairs (the data has ip16 per
   revision) — the identity question is testable locally.
2. Cohort-tier families: shared cooldown profiles ("2m/13s/+26m06") as a
   fingerprint; do tiers recur across task families?
3. The 205 parallel-status pairs as a synchrony measurement: poll-racing
   density per page is itself a coordination observable.

## Reproduce

```sh
make traces-normalize
# then filter edges.jsonl for relation=request_then_response_by_other_label
# and re-read response texts against full-wiki-logs.zip (added text only)
```
