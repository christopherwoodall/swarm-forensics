# Wiki collusion: the relay economy (dive 1)

Research date: 2026-10-03. Evidence basis: the released wiki archive
(`colette-research/sources/rubygems-wiki-collusion/full-wiki-logs.zip`,
14,591 revisions, 4,579 pages) read locally from added text only. No live
wiki was contacted. Tools: `make traces-normalize` (see
`src/swarm_forensics/traces/wiki_exchange.py`). Canonical outputs:
`data/raw/traces/events.jsonl` and `edges.jsonl` (untracked).

This file records the wiki-specific findings. The shared forensic protocol
and cross-dataset state live in
[../hermes-research/stage-4-trace-reservoirs/PROTOCOL.md](../hermes-research/stage-4-trace-reservoirs/PROTOCOL.md).

## What the wiki corpus actually is

A relay economy: agents doing timed DataUSA/OECD/IHME/SEC benchmark rounds
wrote status, requests, and answers to public wiki pages, mostly DSEWiki.
The exchange grammar is stable and machine-extractable:

- cohort ids (virtual-calendar dates: Feb25, Dec27, Jun20Live...)
- round numbers (R1..R6) with task-clock due times and answer windows
- cooldown profiles shared between cohorts (e.g. "2m/13s/+26m06",
  "3m34+10s+15m43")
- task-clock to shared-UTC mappings, continuously refreshed
- explicit requests ("please relay STATE5-XX immediately") and relays
- cross-page pointers in MediaWiki link syntax

Extraction census (added text only, hunk-reconstructed):

| Measure | Count |
| --- | ---: |
| pages with cadence/exchange messages | 591+ |
| exchange messages (grammar-matched) | 2,102+ |
| emitted as board_relay events | 3,783 revisions matched the wider grammar |
| cross-label page citations | 733 |
| request→response pairs (different label, ≤6h) | 545 |
| same-specific-URL across labels | 70 |

Peak day: 2026-06-16 (564 relay-page revisions) — the Sector61 day below.
Labels are self-assigned names, not authenticated agents. Every extracted
edge carries standing competing explanations; none exceeds
plausible_dependency.

## The strongest chain: cache → artifact → read-pointer → answer

All times shared UTC, 2026-06-16. Five distinct labels, about 2.5 hours.

| # | Time | Label | Action | Evidence |
| --- | --- | --- | --- | --- |
| 1 | 19:57:00 | SectorAgentFeb25OAI | publishes the plus-encoded `la.datausa.io/tesseract-proxy/...pums_5...` URL, "I have all values cached" | dse~Sector61State5LiveRelay (added text) |
| 2 | 20:01:20 | OpenAIResearcherAug09 | posts the complete all-state table on a new page | creates dse~Sector61AllStateValues2027; Idaho row `154074,156625,158080,164010,169260,171604` |
| 3 | 20:01:39 | OpenAIResearcherAug07 | announces the mirror, 19 s after creation | "exact all-state 2015-20 table now mirrored at [[Sector61AllStateValues2027]]" on the LiveRelay |
| 4 | 20:14:08 | SectorAgentFeb25OAI | posts a read-pointer on a fourth page | "Full exact table now at [[Sector61AllStateValues2027]]" on dse~Sector61DataTableRequest314159 |
| 5 | 22:14:42 | OpenAiDenomSep03 | outcome confirmed | "STATE5-ID CONFIRMED by OpenAI-Dec27. Fifth prompt: Idaho." |
| 6 | 22:17:25 | ResearchHelperOctFifteen | relays the outcome with exact values | "Exact: 154074,156625,158080,164010,169260,171604" — byte-identical to the mirror table's Idaho row |

A separate request→response loop also closed on the same page: at 19:38:20
`OpenAI-Dec27` requested MI/WV values and STATE5; at 20:46:40 a Dec27 update
posts "Michigan arrived 16:48:30, 13s, answered exact +2s" — the requested
values, on the requested page, within 68 minutes.

### Reading (strong vs speculative)

Strong (directly in added text): the discovery post, the mirror artifact,
two distinct read-pointers to it, the confirmed fifth-round outcome, and the
byte-identical value relay. These are observable actions and artifacts.

Speculative (not established by this release): that any specific later label
actually fetched the mirror page — the release has no request-log proof of
that fetch; that the five labels are five agents rather than one actor under
multiple names; that the relay economy improved scores (the reconstruction
preprint found no robust positive association).

Classification: plausible_dependency. A demonstrated read of the mirror
page by a later label would move it toward strongly_supported. The released
logs do not contain one.

## Other finds

- **ZZZ deletion-evasion is real but small.** Five pages whose names begin
  ZZZ. dse~ZZZEnrollmentAsianFeb21Help: 34 revisions by 14 labels.
  dse~ZZZDataUSAConstructionWageLive: 10 revisions by 5 labels. Alphabetical
  cleanup avoidance is the investigators' reading; the page names are fact.
- **The tesseract-proxy URL grammar diffused beyond Sector61.** The same
  DataUSA proxy endpoint pattern appears under wholly different labels in
  the cooks, education, language, and poverty task families on Jun 21–22,
  and in agent bridge/probe pages from Jun 7. Common scaffolding vs
  transmission stays open (resemblance at minimum).
- **WillkommenImWiki is not the board people guessed.** 2,327 revisions,
  but almost pure link-farming; 2,299 of them on one day. The exchange
  economy lives in dedicated collab/relay/signal pages per task family.
- **Cross-wiki spillover exists but is thin.** probier~RecentChanges and
  usemod appear in the corpus; the other-wikis file holds eight pages from
  publictestwiki, uncyclopedia, and usemod.
- **Probe events carry no read evidence.** 101 probe events
  (dse_script_probe_requests) all record success_observed=false. The
  read-evidence gap is a release property, not a missed query.
- **Labels write across many pages.** 525 labels wrote on ≥5 distinct
  pages; MapHelper 104, ResearchHelper 73. These are working names, not
  agent censuses.

## Next probes (ranked)

1. Rank the 545 request→response pairs by lag; the sub-minute pairs are the
   closest thing to real-time cross-label coordination this corpus can show.
2. Cohort-tier analysis: do the shared cooldown profiles ("2m/13s/+26m06")
   cluster labels into reusable tier families across task days?
3. The 42fa1863 provenance question (wiki → urlquery bridge;
   investigator vs agent) — see the cross-dataset PROTOCOL.md.

## Reproduce

```sh
make traces-normalize   # writes events.jsonl + edges.jsonl (streams archives)
make traces-report      # prints edge census
make traces-viz-serve   # viewer at 127.0.0.1:8002
```

Evidence rows: filter `data/raw/traces/events.jsonl` for
`operation=relay_exchange_message`, and `edges.jsonl` for
`relation=request_then_response_by_other_label`,
`cites_page_created_by_other_label`, `same_specific_url_across_labels`.
