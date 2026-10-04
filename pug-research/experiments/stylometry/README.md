# Stylometry: partitioned lexical comparison of agent text

## Purpose

Measure shared vocabulary between agent-text corpora. Keep partitions separate.
Compare pairs of partitions, not merged monoliths.

## Partitions (OpenAI side)

| Partition | Source (read-only) | Text extracted | Docs | Sampling rule |
|---|---|---|---|---|
| `gems` | `silent-locus/data/processed/gems/` (618 dirs) | Gem directory names plus non-empty `.gemspec`/`.rb`/`.md`/`.txt` files | 618 | All. Names are agent-chosen and carry the signal. |
| `traces` | `silent-locus/openai-agent-traces/data/traces.jsonl` (936 MB) | `source_url`, query parameter names and values, attribution note, tags | ~5% of lines | Every 20th line. Deterministic. |
| `wiki` | `silent-locus/data/2026-05-17-collusion-wiki/raw/revisions.jsonl` (41 MB) | Revision `body` (raw wiki markup, uncleaned) | 14,591 | All. |
| `evals` | `silent-locus/data/2026-10-01-deepsearchqa/questions.jsonl` | Question `problem` text | 900 | All. |

## Exclusions

- `pages.jsonl`: aggregates revision bodies. Including it would double-count wiki text.
- `data/2025-12-04-urlquery-marker-sweep/events.jsonl`: analyst prose, not agent text. Superseded by `traces.jsonl`.
- `labels.jsonl`, `links.jsonl`: metadata, not agent prose.

## AI Village side (blocked)

The `aidigestorg/ai-village` dataset is gated. Access needs manual review.
The VM token returns 401 on all data files. Only the README is public.

Planned partitions (run after access is granted):
- `village_chat`: `chat_messages.jsonl.gz`, grouped by task via `agent_goals`.
- `village_memories`: `agent_memories.jsonl.gz`, grouped by task.
- `village_goals`: `agent_goals.jsonl.gz` (task descriptions).
- `village_code`: `claude_code_messages.jsonl.gz`, grouped by task.
- `village_computer`: `computer_use_turns.jsonl.gz`, grouped by task.

Task grouping uses the goal/task IDs in `agent_goals`. The comparison then
becomes task-vs-task-family, not corpus-vs-corpus.

To proceed: request access at `https://huggingface.co/datasets/aidigestorg/ai-village`,
then run `./fetch_aivillage.sh`. Dataset terms: research and analysis only.
No training without written permission. No re-identification. Cite AI Digest.

## Tokenizers

- `word`: lowercase alphanumeric tokens.
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
