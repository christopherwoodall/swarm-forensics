# Module: Ingest

## 1. Intent & Scope
Acquire raw AI Village data under `data/raw/`. Provide a downloader for the Hugging Face dataset. Provide a writer for synthetic sample tables.

## 2. Active Invariants
- The downloader MUST exclude `images/` and image files.
- The downloader MUST read `HF_TOKEN` from the environment. It MUST NOT print or store the token.
- The downloader MUST pin one commit per run and download into `data/raw/`.
- The downloader MUST check free disk space before it transfers data.
- The downloader MUST NOT extract archives or load a complete table into memory.
- Tests MUST NOT use the network.
- Users MUST start bulk downloads explicitly with `make data-download`.

## 3. Interfaces & Dependencies
- Depends on: `huggingface_hub`, `data/raw/` (untracked output directory).
- Commands (run through `make`):
  - `make data-info`: list files and sizes. No download.
  - `make data-download [TABLES="a b"] [REVISION=<commit>]`: download non-image files.
  - `make data-sample`: write synthetic `agent_goals`, `chat_messages`, and `events` tables to `data/raw/sample/`.
- `download.py`: `select_files`, `parse_tables`, `resolve_dataset`, `download_files`, `main`. Raises `DownloadError`.
- `sample.py`: `build_tables(rows)`, `write_sample(dest, rows)`.
- Output: gzipped JSON Lines files, one per dataset table, plus reference files (`README.md`, `SCHEMA.md`, `CHANGELOG.md`, `manifest.json`, `village-transcript.json`, `example.py`).

## 4. Current State & Known Gaps
- State: Metadata listing verified against the real dataset (19 files, 5.41 GiB). Bulk download not yet run.
- Gap: The sample covers three tables only.
- Gap: Screenshot download is not supported.
- Gap: Downloaded files are not checked against a checksum.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-01 Droid]: User approved all non-image files. This replaces the three-table limit in `AGENTS.md`.
