# Dataset Morphology: Stage 0

Status: Implemented for the supported text formats.
Specification: [SPEC.md](SPEC.md).

## Purpose

Stage 0 describes a corpus before pattern discovery begins.
It reports observed structure without classifying a swarm or agent.
It does not modify source files.

## Supported inputs

- `.jsonl` and `.ndjson` files contain one JSON object per nonblank line.
- `.csv` files contain one record per data row.
- Each supported format MAY use gzip compression with a `.gz` suffix.
- A directory scan recurses through non-symlink directories.
- A directory scan counts unsupported files by extension and does not open them.
- A malformed supported file stops the inventory without a partial report.
- JSON arrays, Parquet, databases, and other formats remain unsupported.
- Nested JSON objects use JSON Pointer paths; arrays remain atomic fields.
- Empty CSV cells remain empty strings because CSV defines no null marker.

## Report contents

The report includes record counts, source names, formats, and ignored-file counts.
It lists fields, types, missingness, null counts, and string-length ranges.
It marks candidate actor and artifact identifiers from field names only.
It marks content, link, lineage, and session-boundary field candidates.
It reports candidate timestamp coverage, parse quality, and timezone quality.
It labels event or snapshot structure as a low-confidence field-name hypothesis.
It counts exact canonical-record duplicates and leaves derivation unclassified.

## Privacy and uncertainty

The report MUST NOT contain record text or record field values.
The report MAY contain source-relative file names and field names for provenance.
Diagnostics MUST NOT contain record values.
Temporary SQLite tables store hashes and field paths, not record values.
Candidate identifiers MUST NOT be read as verified actor identities.
Timestamp ranges MUST keep timezone-naive values separate from aware values.
Unit hypotheses MUST NOT classify individual records.
Exact duplicates MUST NOT be treated as proof of copied or derived data.

## Downstream handoff

Stage 0 emits an inventory, not a candidate morphology card.
Later discovery stages MUST construct the complete card defined in `SPEC.md`.
The `pug-scratch` plugin accepts complete cards through `POST /api/plugins/swarm-forensics/morphologies`.
Operators MAY paste a complete card into the plugin's Morphologies tab.
Import does not start a hunt or promote an IOC.
The upstream analyzer-to-plugin client remains unimplemented.

## Run

Run `make morphology-inventory MORPHOLOGY_INPUT=<file-or-directory>`.
Add `MORPHOLOGY_OUTPUT=colette-research/dataset-morphology/inventory.json` to save a report.
The default output is JSON on standard output.
Use synthetic fixtures for tests; do not include corpus values in tracked reports.

No external corpus has been inventoried in this implementation slice.
The next slice SHOULD normalize traceable records without changing source evidence.
