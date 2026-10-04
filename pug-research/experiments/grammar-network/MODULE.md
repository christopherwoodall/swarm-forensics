# Module: Grammar Network (pug-research)

## 1. Intent & Scope
Test STRUCTURAL convergence between agent-text partitions where bag-of-words
stylometry found lexical divergence (disjoint cores; wiki as stylistic
island). Two builds:
- Build A: windowed co-occurrence grammar networks per partition, compared on
  graph metrics (degree distribution, clustering, centrality) — not shared
  vocabulary.
- Build B: the hunt's URL/request construction grammar formalized as a typed
  graph (hosts, path grammars, param names, nonce templates, relay chains,
  jq ops). This graph is the harness/toolkit fingerprint.
Read [REPORT.md](REPORT.md) for findings and [README.md](README.md) for
provenance and sampling rules.

## 2. Active Invariants
- Memory-safe stream processing: never load full raw archives into memory.
  Sample with deterministic strides; record every sampling rule.
- No tagger available on this VM (no spacy/nltk): Build A uses windowed
  co-occurrence as the documented fallback, plus tagger-free structural
  prose features (sentence length, punctuation profile, list markers,
  URL density, imperative frames).
- Raw downloads stay untracked under `data/raw/`. Processed outputs
  (`networks.json`, `request_grammar.json`, logs) are committed.
- Every run is logged to `runs_log.jsonl` with parameters. Degenerate runs
  stay in the log, marked superseded — never deleted.
- Graph code is standard library only: sparse dict-of-dict adjacency,
  hand-rolled power iteration, least-squares and Pearson. No numpy/scipy,
  no networkx, no tagger on this VM.

## 3. Interfaces & Dependencies
- Dependencies: Python 3 standard library only (sqlite3, gzip, json, re,
  math, statistics). No numpy/scipy, no tagger, no networkx.
- `extract_code_text.py`: Ruby comment/string extraction from the gem corpus
  -> `data/processed/gems_code_nl.jsonl` (one doc per gem).
- `build_a.py`: co-occurrence networks + graph metrics + structural prose
  features -> `networks.json`.
- `build_b.py`: request-grammar graph from sampled trace URLs ->
  `request_grammar.json`.
- Commands: root Makefile target `grammar-net` (MODE=a|b|code|all).
- Reads (read-only): silent-locus wiki revisions, deepsearchqa questions,
  gem corpus, openai-agent-traces; stylometry `data/raw/` village tables.

## 4. Current State & Known Gaps
- State: both builds implemented; runs logged; REPORT.md written.
- Gap: no POS tagger — dependency-grammar networks are not built. Windowed
  co-occurrence is a weaker structural proxy; say so when citing results.
- Gap: village `computer_use_turns` was still downloading when Build A ran;
  it is not a partition here.
- Gap: Build B covers URL/request grammar only. Header/cookie grammar and
  POST-body grammar are unmeasured.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-04 Subagent]: Lane is standard library only (review #17 was
  right about the docs; the numpy was real but has been removed). No
  numpy/scipy/networkx/tagger anywhere in the lane.
- [2026-10-04 Subagent]: gems-code-nl extraction and Build A skip gracefully
  when the gems source is absent (audit may remove it); logged, never crash.
- [2026-10-04 Subagent]: Pattern DB + behavioral experiments use plain
  counts (frequencies, conditional probabilities, Markov, CV) over SOTA
  methods, per user steer; every run logged.
