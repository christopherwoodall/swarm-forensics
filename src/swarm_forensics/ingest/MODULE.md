# Module: Ingest

## 1. Intent & Scope
Acquire raw AI Village data under `data/raw/`. Provide a downloader for the Hugging Face dataset. Provide a writer for synthetic sample tables.

## 2. Active Invariants
- The downloader MUST exclude `images/` and image files.
- The downloader MUST read `HF_TOKEN` from the environment. It MUST NOT print or store the token.
- The downloader MUST pin one commit per run and download into `data/raw/`.
- The downloader MUST check free disk space before it transfers data.
- The downloader MUST NOT extract archives or load a complete table into memory.
- Raw validation MUST preserve unknown fields. Diagnostics MUST NOT contain record values.
- Raw validation MUST stream one record at a time and MUST NOT load a complete table.
- Tests MUST NOT use the network.
- Users MUST start bulk downloads explicitly with `make data-download`.

## 3. Interfaces & Dependencies
- Depends on: `huggingface_hub`, `jsonschema`, `data/raw/` (untracked output directory).
- Commands (run through `make`):
  - `make data-info`: list files and sizes. No download.
  - `make data-schema [REVISION=<commit>]`: download only `SCHEMA.md`, `CHANGELOG.md`, and `manifest.json`.
  - `make data-download [TABLES="a b"] [REVISION=<commit>]`: download non-image files.
  - `make data-sample`: write synthetic `agent_goals`, `chat_messages`, and `events` tables to `data/raw/sample/`.
  - `make data-validate [DATA_DIR=<dir>] [TABLES="a b"] [LIMIT=<n>]`: validate tables against the schema. Defaults: `data/raw/sample/`, 100 records per table. `LIMIT=0` scans every record.
- `download.py`: `select_files(files, tables, schema_only)`, `SCHEMA_FILES`, `parse_tables`, `resolve_dataset`, `download_files`, `main`. Raises `DownloadError`.
- `sample.py`: `build_tables(rows)`, `write_sample(dest, rows)`.
- `dataset.schema.json`: JSON Schema Draft 2020-12. One definition per table under `$defs`. `x-tables` lists the tables. `x-references` annotates joins. `x-source` records the reference revision.
- `schema.py`: `load_schema`, `table_names`, `validator_for`, `validate_record(table, record, line)`, `iter_records(path, table, limit)`, `check_table`, `main`. Raises `DatasetError` with table, line, field path, and rule.
- Output: gzipped JSON Lines files, one per dataset table, plus reference files (`README.md`, `SCHEMA.md`, `CHANGELOG.md`, `manifest.json`, `village-transcript.json`, `example.py`).

## 4. Current State & Known Gaps
- Historical: Earlier work reported a completed bulk download and bounded real-data validation. This session did not reproduce those results.
- State: This checkout lacks the root raw tables and upstream reference bodies. Synthetic samples remain available.
- State: Public metadata confirms 13 table configurations at revision `838b4150303ca8228e8edb432d8b8ccae353d258`.
- State: All 13 tables have a contract. Its recorded revision matches current public metadata. No full scan has run.
- State: Read the [structure report](../../../colette-research/notes/ai-village-dataset-structure.md) for the file census and evidence limits.
- Gap: `HF_TOKEN` is unset in this session. Gated records, schema text, and changelog text were not inspected.
- State: `--schema-only` selection covers three reference files.
- Gap: Contracts use `SCHEMA.md` plus bounded field-type inspection. `SCHEMA.md` omits `chat_rooms` name lists, `villages.is_chat_open`, `villages.schedule`, and `claude_code_messages.message_uuid`.
- Gap: Event payloads are typed per field only. No per-action required fields exist. `startDay` and `endDay` are untyped.
- Gap: Foreign keys, event ordering, and the village transcript are not validated.
- Gap: The sample covers three tables only.
- Gap: Screenshot download is not supported.
- Gap: Downloaded files are not checked against a checksum.

## 5. Pruned Decisions (Keep max 3)
- [2026-10-03 Hermes]: Separate public file metadata from raw-record evidence. Preserve earlier validation reports as historical claims.
- [2026-10-01 Droid]: Add JSON Schema contracts and streaming validation before parsers. Contracts allow unknown fields and keep required fields minimal.
- [2026-10-01 Droid]: User approved all non-image files. This replaces the three-table limit in `AGENTS.md`.
