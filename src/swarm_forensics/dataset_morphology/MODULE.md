# Module: Dataset Morphology

## 1. Intent & Scope

Build dataset-agnostic reconnaissance for future morphology discovery.
Stage 0 inventories records, fields, identifiers, timestamps, links, and boundaries.
The inventory generates research leads. It does not detect swarms.

## 2. Active Invariants

- Readers MUST stream one record at a time.
- Temporary SQLite tables MUST store hashes, not record values.
- Reports MUST NOT contain record text or record field values.
- Reports MAY contain source-relative file names and field names for provenance.
- Candidate identifiers MUST remain field-name hypotheses.
- Unit labels MUST remain low-confidence field-name hypotheses.
- Readers MUST fail the inventory when a supported source is unreadable.
- Readers MUST report ignored file counts and extensions.
- Readers MUST retain naive timestamps without timezone conversion.
- JSON arrays MUST remain unsupported until a streaming reader exists.

## 3. Interfaces & Dependencies

- `inventory.py`: `inventory_dataset(path)` returns a value-free JSON-compatible report.
- `inventory.py`: CLI accepts a file or directory and optional `--output` path.
- `make morphology-inventory`: runs the Stage 0 inventory through the project environment.
- Supported formats: `.jsonl`, `.ndjson`, `.csv`, and their `.gz` variants.
- Directory scans recurse through non-symlink directories and count unsupported files.
- Each JSONL or NDJSON object line defines one record.
- Each CSV data row defines one record; empty cells remain empty strings.
- Nested JSON objects use RFC 6901 pointers; arrays remain atomic fields.
- The implementation uses Python standard-library modules only.

## 4. Current State & Known Gaps

- Verified: Stage 0 inventories field presence, missingness, types, and string lengths.
- Verified: It reports candidate identifiers, content fields, link fields, and boundaries.
- Verified: It reports timestamp coverage, parse quality, timezone quality, and ranges.
- Verified: It counts exact canonical-record duplicates using temporary digest storage.
- Verified: It reports possible event or snapshot markers without classifying records.
- Gap: JSON arrays, Parquet, databases, and other input formats are unsupported.
- Gap: Nested objects inside arrays are not inspected.
- Gap: Derived or cumulative records are not inferred from exact duplicates.
- Gap: Pattern families, morphology matches, scores, and candidate cards remain unimplemented.

## 5. Decisions (Keep max 3)

- [2026-10-04 Hermes]: Support streamable text formats first; preserve value privacy and observable-unit uncertainty.
