"""Validate AI Village table records against the bundled JSON Schema contracts.

Usage: python -m swarm_forensics.ingest.schema [--dir DIR] [--tables TABLE ...] [--limit N]

The command needs no network access. It reads each table one line at a time.
Diagnostics name the table, line, field path, and rule. They MUST NOT contain record values.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import zlib
from collections.abc import Iterator
from functools import cache, lru_cache
from pathlib import Path
from typing import Any, NamedTuple

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).with_name("dataset.schema.json")
DEFAULT_DIR = Path("data/raw/sample")
DEFAULT_LIMIT = 100
DIALECT = "https://json-schema.org/draft/2020-12/schema"


class DatasetError(Exception):
    """Raised for a failed check. The message MUST NOT contain record values."""

    def __init__(self, subject: str, reason: str, line: int | None = None, path: str | None = None):
        self.subject = subject
        self.reason = reason
        self.line = line
        self.path = path
        parts = [subject]
        if line is not None:
            parts.append(f"line {line}")
        if path:
            parts.append(path)
        parts.append(reason)
        super().__init__(": ".join(parts))


class TableReport(NamedTuple):
    table: str
    checked: int
    complete: bool  # True when the scan reached the end of the file.


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    """Return the bundled schema document. Callers MUST NOT change it."""
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def table_names() -> tuple[str, ...]:
    """Return the names of the tables that have a contract."""
    return tuple(load_schema()["x-tables"])


def table_file(directory: Path, table: str) -> Path:
    """Return the path of the table archive in `directory`."""
    return directory / f"{table}.jsonl.gz"


@cache
def validator_for(table: str) -> Draft202012Validator:
    """Return the validator for one table. References resolve inside the bundled document."""
    if table not in table_names():
        raise DatasetError(table, "unknown table")
    schema = {"$schema": DIALECT, "$defs": load_schema()["$defs"], "$ref": f"#/$defs/{table}"}
    return Draft202012Validator(schema)


def _path_text(parts: list[Any]) -> str:
    text = "$"
    for part in parts:
        text += f"[{part}]" if isinstance(part, int) else f".{part}"
    return text


def _error_key(error: Any) -> list[str]:
    return [str(part) for part in error.absolute_path]


def _describe(error: Any) -> tuple[str, str]:
    """Return the field path and rule name. The path uses schema names, never record values."""
    parts = list(error.absolute_path)
    rule = str(error.validator)
    if rule == "required":
        missing = [name for name in error.validator_value if name not in error.instance]
        parts.append(missing[0])
    return _path_text(parts), rule


def validate_record(table: str, record: Any, line: int | None = None) -> None:
    """Raise DatasetError when `record` breaks the contract of `table`."""
    validator = validator_for(table)
    if validator.is_valid(record):
        return
    error = min(validator.iter_errors(record), key=_error_key)
    path, rule = _describe(error)
    raise DatasetError(table, f"rule '{rule}' failed", line, path)


def _read_lines(path: Path, table: str) -> Iterator[tuple[int, str]]:
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            yield from enumerate(handle, start=1)
    except FileNotFoundError:
        raise DatasetError(table, "file not found") from None
    except (OSError, EOFError, zlib.error, UnicodeDecodeError):
        raise DatasetError(table, "damaged or unreadable gzip archive") from None


def iter_records(path: Path, table: str, limit: int | None = None) -> Iterator[dict[str, Any]]:
    """Yield validated records one at a time. Stop after `limit` records when it is set.

    Raise DatasetError for a missing file, a damaged archive, malformed JSON,
    or a record that breaks the contract. Unknown fields stay in the record.
    """
    if limit is not None and limit <= 0:
        return
    count = 0
    for number, line in _read_lines(path, table):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except ValueError:
            raise DatasetError(table, "malformed JSON", number) from None
        validate_record(table, record, number)
        yield record
        count += 1
        if limit is not None and count >= limit:
            return


def check_table(path: Path, table: str, limit: int | None = None) -> TableReport:
    """Validate up to `limit` records. Report whether the scan reached the end of the file."""
    wanted = None if limit is None else limit + 1
    count = sum(1 for _ in iter_records(path, table, wanted))
    if limit is not None and count > limit:
        return TableReport(table, limit, False)
    return TableReport(table, count, True)


def resolve_tables(directory: Path, requested: list[str] | None) -> list[str]:
    """Return the tables to check. Raise DatasetError for a missing file or an empty selection."""
    if requested:
        tables = list(dict.fromkeys(requested))
        for table in tables:
            if not table_file(directory, table).is_file():
                raise DatasetError(table, f"file not found in {directory}")
        return tables
    tables = [table for table in table_names() if table_file(directory, table).is_file()]
    if not tables:
        raise DatasetError(str(directory), "no supported table files found")
    return tables


def run(directory: Path, requested: list[str] | None, limit: int | None) -> None:
    """Validate the selected tables and print one line per table."""
    limited = False
    tables = resolve_tables(directory, requested)
    for table in tables:
        report = check_table(table_file(directory, table), table, limit)
        status = "reached end of file" if report.complete else f"stopped at limit {limit}"
        print(f"{table}: {report.checked} records checked, {status}")
        limited = limited or not report.complete
    print(f"Validated {len(tables)} tables in {directory}.")
    if limited:
        print("The check was limited. It does not cover the whole dataset. Use LIMIT=0 for all rows.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="default: data/raw/sample")
    parser.add_argument(
        "--tables", nargs="+", metavar="TABLE", choices=table_names(), help="default: all present"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="records per table (default: 100). Use 0 to scan every record.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit MUST NOT be negative")
    try:
        run(args.dir, args.tables, args.limit or None)
    except DatasetError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
