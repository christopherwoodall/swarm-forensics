# Module: Traces

## 1. Intent & Scope

Normalize the three external trace reservoirs in `colette-research/sources/`
(URLQuery, Arquivo.pt via the us-canada evidence package, and the
RubyGems/wiki-collusion corpus) into one cross-dataset event table and
candidate edge table under `data/raw/traces/`.

The subsystem is governed by the shared forensic protocol at
`colette-research/hermes-research/stage-4-trace-reservoirs/PROTOCOL.md`.
That protocol, not this module, defines the ten coordination-capacity
questions, the eight-way evidence distinctions, and the five-level edge
taxonomy.

## 2. Active Invariants

- Readers MUST stream archives one record at a time. A reader MUST NOT load a
  complete archive into memory.
- Every event row MUST carry a raw reference that identifies the exact source
  record (file, record id, or row number).
- A row MUST NOT assert an agent identity, a successful remote effect, or a
  causal transfer. Identity is `actor_hint`, never `actor_id`.
- Optional-text fields (`parent_event`, `notes`, `artifact`) MAY be empty.
  Enum fields MUST use their declared vocabulary.
- Wiki evidence MUST use added-text reconstruction, never cumulative page
  copies. Citation counting MUST count only citations in added text.
- Edges MUST carry `causal_strength` plus `competing_explanation`. Ambiguous
  cases go to the unresolved ledger (`edges.jsonl` rows with
  `causal_strength=temporal_structural_association_only` or weaker), not the
  graph.
- Bridge probes MUST keep identity linkage, common harness, common task,
  common operator, and direct transfer as separate competing hypotheses.

## 3. Interfaces & Dependencies

- Depends on: stdlib only (`csv`, `gzip`, `json`, `re`, `zipfile`,
  `hashlib`). No new external dependencies.
- `schema.py`: `EVENT_FIELDS`, `EDGE_FIELDS`, `EVENT_ACTIONS`,
  `EDGE_STRENGTHS`, `DATASETS`, `TECHNIQUE_FAMILIES`,
  `VALID_ACTOR_HINTS`, `validate_event(row)`, `validate_edge(row)`.
  `task_family` is a first-class event field; `TECHNIQUE_FAMILIES` splits
  the former `unknown` into `no_visible_mechanism` (row parsed, no
  coordination-relevant mechanism visible) and `content_not_in_release`
  (released record withholds request shape), reserving `unknown` for
  unexamined rows.
- `taskfamilies.py`: `task_family_for(target_url)` — coarse host/path
  template labels for arquivo and urlquery-http targets (visible request
  structure, not a mechanism claim). Host-only fallback keeps coverage
  honest.
- `rows.py`: `mk_event(...)`, `mk_edge(...)`, `added_text(rev)`,
  `actor_hint_for_label(label)`, `short(text)`, `hash_prefix(text)`.
- `readers.py`: `iter_wiki_revisions`, `iter_wiki_events`,
  `iter_gem_records`, `technique_family_for(url)`.
- `wiki.py`: `wiki_event_rows(zip_path)` — revisions and events, added-text
  reconstruction, investigator labels mapped to `actor_hint=investigator`.
- `arquivo.py`: `arquivo_event_rows(uscan_zip)` — capture rows with zz=
  nonce preservation; `uscan_response_rows(uscan_zip)` — the investigation's
  fresh-response layer, actor_hint=investigator.
- `reservoirs.py`: `gem_event_rows(records_gz)` — registry_metadata as
  register events, package_member as publish events;
  `urlquery_event_rows(uq_zip)` — catalog request events;
  `urlquery_http_rows(uscan_zip)` — report-level HTTP exports inside the
  us-canada package.
- `bridges.py`: `gem_wiki_overlap_edges` — exact URL overlap via gem
  homepage sha256 against wiki link sha256 (the "radioactive marble" probe);
  `urlquery_citation_edges` — wiki added-text citations of urlquery reports;
  `shared_relay_edges` — relay hosts named in both populations.
- `wiki_exchange.py`: relay-exchange extraction — `extract_messages`,
  `exchange_event_rows`, `all_exchange_edges` (citation edges,
  request→response edges, URL-recurrence edges). Grammar-based; added text
  only; every edge carries standing competing explanations.
- `cli.py`: `run(out_dir)`, `main(argv)`. Writes `events.jsonl`,
  `edges.jsonl`.
- `report.py`: prints per-dataset counts, actor hints, technique families,
  and every edge with competing explanation.
- `viz.py`: `build_summary(events_path, edges_path)`, `main(argv)`.
  Streams both tables and writes the compact viewer aggregate
  `data/viz_mock/v4_traces/data/viewer-data.json` (totals, daily stacked
  counts, families, hints, time bounds, top targets, zz-nonce recurrence,
  gem stems, verbatim edges). Never loads a complete table into memory.
- Viewer (not a package): `data/viz_mock/v4_traces/` — `index.html`
  (self-contained, no remote dependencies) and `serve.py` (loopback,
  serves the viewer directory plus one `GET /api/events` endpoint that
  streams bounded queries against `data/raw/traces/events.jsonl` with
  substring prefilters; matches capped at 200 rows).
- Commands (run through `make`):
  - `make traces-normalize` — write `data/raw/traces/events.jsonl` and
    `edges.jsonl` from the real archives.
  - `make traces-report` — print cross-dataset summaries and edges.
  - `make traces-viz-build [TRACES_PORT]` — write the viewer aggregate.
  - `make traces-viz-serve` — serve the viewer on 127.0.0.1:8002.
- Tests: `test_traces.py` — schema validation, URL classification, label
  mapping, added-text reconstruction, viz aggregation. Offline; no raw
  archives, no network.

## 4. Current State & Known Gaps

- State: normalization and bridge probes run over the full real archives:
  646,982 events (arquivo 561,298; urlquery 47,316; wiki 38,287; rubygems 81)
  and 1,369 candidate edges. All rows pass schema validation.
- State: wiki relay-exchange extraction adds 3,783 board_relay events
  (cadence messages: cohort ids, R-rounds, task clocks, UTC mappings) and
  1,348 wiki edges: 733 cross-label page citations, 545 request→response
  pairs, 70 same-URL-across-labels. All classified plausible_dependency or
  weaker, with standing competing explanations (labels are not identities).
- State: hand-traced strongest chain (in PROTOCOL.md): Feb25 BREAKTHROUGH
  proxy URL (19:57) → AllStateValues2027 mirror table (20:01) → cross-label
  pointer by a third label (20:01:39) → STATE5-ID confirmed by Dec27 (22:14)
  → exact Idaho values relayed by a fifth label (22:17).
- State: technique families now split the former `unknown` bucket:
  `no_visible_mechanism` 517,438; `content_not_in_release` 37,718 (urlquery
  catalog rows plus the investigation's fresh-response layer). No row remains
  `unknown`.
- State: `task_family` labels cover 643,130 of 643,199 events (91 families;
  only the 69 arquivo investigator read rows are unlabeled). Top families:
  crdc_state_estimation 213,638; md_reportcard_2022_download 147,759;
  urlquery_report_catalog 37,649; kansas_memory 36,579.
- State: ten exact-URL overlaps between gem homepages and wiki link rows
  (resemblance_only; transmission not established). One wiki→urlquery
  citation (temporal_structural_association_only; investigator provenance is
  a live competing explanation).
- Gap: task-family templates are derived from the us-canada package's own
  target set; hosts outside it fall back to `host:<name>` labels (448+ rows
  under googletagmanager etc. are page-asset noise, correctly isolated in
  their own host bucket).
- Gap: the unresolved ledger is folded into `edges.jsonl` by strength class;
  a separate ledger file is not yet written.
- Gap: no burst or feedback analysis within arquivo task families yet (the
  remaining request-ecology probe). No per-path nonce-recurrence table is
  emitted.
- Gap: no observed_read/behavior_change values beyond the defaults; response
  bodies are absent from all three packages, so read evidence stays
  unobserved by construction.
- Gap: no cross-dataset family analysis beyond the three implemented probes.

## 5. Pruned Decisions (Keep max 3)

- [2026-10-03 Hermes]: Split `unknown` into `no_visible_mechanism` vs `content_not_in_release`, and carry `task_family` separately from `technique_family`. A coarse request template is visible structure, not a mechanism claim; conflating them would re-inflate the unknowns dishonestly.
- [2026-10-03 Hermes]: Keep gem↔wiki URL overlap at resemblance_only; identical relay URLs establish shared task material at most, and transmission requires a demonstrated read that no released record provides.
- [2026-10-03 Hermes]: Wiki attribution discipline: count only added-text citations (inherited page copy manufactures propagation), and map investigator-provenance labels to actor_hint=investigator rather than dropping them (dropping would silently re-weight the agent-label population).
