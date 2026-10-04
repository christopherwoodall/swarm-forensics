# Grammar Network (pug-research)

Structural comparison where bag-of-words stylometry found lexical divergence.
See [MODULE.md](MODULE.md) for invariants and [REPORT.md](REPORT.md) for findings.

## Builds

- **Build A** (`build_a.py`): windowed co-occurrence networks per text
  partition. No POS tagger on this VM (no spacy/nltk) — windowed
  co-occurrence is the documented fallback. Compares partitions on graph
  metrics (degree-distribution exponent, clustering, eigenvector
  centrality, assortativity) plus tagger-free structural prose features
  (sentence length, punctuation profile, list markers, URL density,
  imperative-sentence rate). Partitions: `wiki`, `evals`, `gems-code-nl`,
  `v-chat` (village agent chat), `v-mem` (village memories), `v-goals`
  (village goals), `v-code` (village Claude Code messages). The
  URL-metadata `traces` partition is excluded (non-linguistic).
- **Build B** (`build_b.py`): the request-construction grammar as a typed
  graph. Nodes: hosts, relays, path-segment grammars, param names, nonce/tag
  templates, jq ops. Edges: co-occurrence in one request + relay-nesting
  chain transitions. Sources: openai-agent-traces (1-in-20) + wiki-body URLs
  (1-in-5, where the relay layer lives). This graph is the harness
  fingerprint.
- **Code-embedded text** (`extract_code_text.py`): Ruby comments, string
  literals, gemspec descriptions from the 618 gem dirs ->
  `data/processed/gems_code_nl.jsonl` (the `gems-code-nl` partition).

## Outputs

- `networks.json` — per-partition graph metrics + top central nodes
- `request_grammar.json` — typed request-grammar graph + fingerprint summary
- `runs_log.jsonl` — every run with parameters; degenerate runs stay logged

## Sampling rules

Build A streams all sources; village chat stride 5, Claude Code stride 5,
goals unstrided (n=33). v-mem is excluded by default (p50 doc 17KB makes
co-occurrence compute-prohibitive on this VM). Co-occurrence pass caps at
4000 tokens per doc.
Build B: traces stride 20, wiki bodies stride 5. Structural features
computed on the first 400 docs per partition (4k chars cap each).

## Provenance

Read-only on: `silent-locus/data/2026-05-17-collusion-wiki`,
`silent-locus/data/2026-10-01-deepsearchqa`,
`silent-locus/data/processed/gems`,
`silent-locus/openai-agent-traces/data/traces.jsonl`,
`stylometry/data/raw/` (AI Village tables, gated HF dataset).
Raw downloads stay untracked under `data/raw/`.

## Commands

This lane owns its Makefile; the repo root delegates to it (`make grammar-net`).

- `make extract`: extract natural language from inside source code.
- `make a`: Build A, syntactic co-occurrence networks per partition.
- `make b`: Build B, request-construction grammar graph.
- `make all`: the full lane, extract through both builds.
