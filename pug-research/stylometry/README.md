# Stylometry: partitioned lexical comparison of agent text

## Purpose

Measure shared vocabulary between agent-text corpora. Keep partitions separate.
Compare pairs of partitions, not merged monoliths.

## Partitions (OpenAI side)

| Partition | Source (read-only) | Text extracted | Docs | Sampling rule |
|---|---|---|---|---|
| `gems_names` | `silent-locus/data/processed/gems/` (617 dirs, `oai-1.3.0` excluded) | Directory names only (agent-chosen) | 617 | All |
| `traces` | `silent-locus/openai-agent-traces/data/traces.jsonl` (936 MB) | `source_url`, query parameter names and values, attribution note, tags | ~5% of lines | Every 20th line. Deterministic. |
| `traces_clean` | same | `source_url`, query parameter names/values only (no analyst notes/tags) | ~5% of lines | Every 20th line. Deterministic. |
| `wiki` | `silent-locus/data/2026-05-17-collusion-wiki/raw/revisions.jsonl` (41 MB) | Revision `body` (raw wiki markup, uncleaned) | 14,591 | All. |
| `evals` | `silent-locus/data/2026-10-01-deepsearchqa/questions.jsonl` | Question `problem` text | 900 | All. |

Removed: `gems_code` (740 files, median 1 byte — empty scaffolds; zero
provider markers after the `oai-1.3.0` exclusion; bust per partition audit,
2026-10-04). The mixed `gems` partition is superseded by `gems_names`.

## AI Village side (data landed 2026-10-04)

All five tables in `data/raw/` (gated; downloaded with granted access):
`chat_messages.jsonl.gz` (52 MB), `agent_memories.jsonl.gz` (1.9 GB),
`agent_goals.jsonl.gz` (33 goals), `claude_code_messages.jsonl.gz` (104 MB),
`computer_use_turns.jsonl.gz` (2.47 GB; first download was truncated at
2.0 GB — gzip EOFError — resumed via HTTP 206 and verified with `gzip -t`).

Functionally-matched v2 partitions (see `build_lexdb_v2.py`). Large village
partitions use deterministic 1-in-N systematic sampling (same principle as
the v1 traces 1-in-20; full builds infeasible on the shared 2-CPU box):
- `ours_wiki` ↔ `vil_chat_agent` (speaker_type='agent' only, 1-in-5;
  `vil_chat_all` 1-in-5 kept for the contamination check)
- `ours_evals` ↔ `vil_goals` (33 goals, all)
- `ours_gems_names` ↔ `vil_code` (claude_code assistant messages, 1-in-5)
- `ours_traces` / `ours_traces_clean` ↔ `vil_computer_lex` (1-in-20)
- `vil_memories` — village-only reference, 1-in-10 (long-horizon agent voice)

## Tokenizers

- `word`: lowercase alphanumeric tokens (percent-decoded first).
- `subword`: case/digit/separator splits + greedy morpheme splitting on long
  (>=10 char) tokens — `agentoaitestabc123` → `agent oai test abc 123`.
  Morpheme list is documented in `build_lexdb.py`; ordinary English words are
  never over-split (length gate).
- `char4`: character 4-grams. Robust to deliberate obfuscation.
- `funcwords`: function words only. Style signal without topic signal.

## Methods (`compare.py`)

- `jaccard_topn`: Jaccard on top-N vocabularies.
- `cosine_tfidf`: cosine on TF-IDF vectors (IDF over all partitions).
- `keyness`: log-likelihood G2 distinctive terms per side.
- `spearman`: rank correlation of frequencies on shared terms.
- `shared_ngrams`: Jaccard on top-N bigrams and trigrams.
- `burrows_delta`: Burrows Delta on top-N frequent words.
- `char_cosine`: cosine on character 4-gram vectors.

## Commands

This lane owns its Makefile; the repo root delegates to it.
Run from this directory, or from the root as `make stylo-*`.

- `make download`: fetch the AI Village tables (`HF_TOKEN` required).
- `make lexdb`: build `lexdb.sqlite`.
- `make lexdb-v2`: build the functionally-matched `lexdb_v2.sqlite`.
- `make compare MATRIX=1`: run the full preset matrix across all pairs.
- `make compare PAIR="wiki evals"`: run one pair with one method.
- `make actions`: action-type distributions and transitions.
- `make all`: the full lane, download through actions.
- Every run appends to `runs_log.jsonl` with parameters and results.

## Files

- `build_lexdb.py`: streaming partition builder. Writes `lexdb.sqlite`.
- `compare.py`: multi-method comparison and run logger.
- `fetch_aivillage.sh`: village data downloader (needs granted access).
- `lexdb.sqlite`: build artifact. Untracked. Regenerate with `make stylo-lexdb`.
- `runs_log.jsonl`: every run's parameters and results. Tracked.
- `data/raw/`: village downloads land here. Untracked.
- `REPORT.md`: findings.
- `MODULE.md`: module invariants and state.
