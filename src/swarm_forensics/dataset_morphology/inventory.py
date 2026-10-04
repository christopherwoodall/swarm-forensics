"""Build a streaming reconnaissance report for JSONL, NDJSON, and CSV datasets.

The report describes observable fields. It does not infer agent identity or coordination.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
import tempfile
import zlib
from collections import Counter
from collections.abc import Iterator, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

UTC = timezone.utc
ACTOR_TOKENS = {
    "account",
    "actor",
    "agent",
    "author",
    "bot",
    "human",
    "model",
    "participant",
    "persona",
    "person",
    "process",
    "speaker",
    "user",
    "worker",
}
ARTIFACT_TOKENS = {
    "artifact",
    "branch",
    "comment",
    "document",
    "event",
    "file",
    "memory",
    "message",
    "object",
    "package",
    "page",
    "post",
    "record",
    "repo",
    "repository",
    "resource",
    "state",
    "task",
}
TIMESTAMP_TOKENS = {"date", "datetime", "time", "timestamp", "ts"}
CONTENT_TOKENS = {
    "body",
    "code",
    "comment",
    "content",
    "description",
    "input",
    "message",
    "output",
    "prompt",
    "response",
    "stderr",
    "stdin",
    "stdout",
    "summary",
    "text",
    "title",
}
LINK_TOKENS = {
    "artifact",
    "branch",
    "conversation",
    "edge",
    "file",
    "link",
    "message",
    "next",
    "parent",
    "prev",
    "reference",
    "ref",
    "reply",
    "repo",
    "run",
    "session",
    "source",
    "target",
    "task",
    "thread",
    "url",
}
BOUNDARY_TOKENS = {
    "channel",
    "conversation",
    "job",
    "room",
    "run",
    "session",
    "task",
    "thread",
    "workflow",
}
EVENT_TOKENS = {"action", "command", "event", "operation", "tool_call", "verb"}
SNAPSHOT_TOKENS = {"current", "revision", "snapshot", "state", "status", "version"}
LINEAGE_TOKENS = {
    "derived_from",
    "lineage",
    "parent",
    "previous",
    "prev",
    "revision",
    "sequence",
    "source_id",
    "supersedes",
    "version",
}


class InventoryError(Exception):
    """Raised when the input cannot be inventoried without exposing record values."""

    def __init__(self, subject: str, reason: str, row: int | None = None):
        self.subject = subject
        self.reason = reason
        self.row = row
        parts = [subject]
        if row is not None:
            parts.append(f"row {row}")
        parts.append(reason)
        super().__init__(": ".join(parts))


def _path_name(name: str) -> str:
    """Return one JSON Pointer segment with RFC 6901 escaping."""
    return name.replace("~", "~0").replace("/", "~1")


def _flatten(record: Mapping[str, Any]) -> Iterator[tuple[str, Any]]:
    """Yield object fields as JSON Pointer paths. Keep arrays atomic."""
    def visit(value: Mapping[str, Any], prefix: str) -> Iterator[tuple[str, Any]]:
        for name, item in value.items():
            field_path = f"{prefix}/{_path_name(name)}"
            yield field_path, item
            if isinstance(item, dict):
                yield from visit(item, field_path)

    yield from visit(record, "")


def _leaf_name(field_path: str) -> str:
    """Return a normalized field name from a JSON Pointer."""
    leaf = field_path.rsplit("/", 1)[-1].replace("~1", "/").replace("~0", "~")
    leaf = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", leaf).lower()
    return leaf


def _tokens(field_path: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", _leaf_name(field_path)))


def _context_tokens(field_path: str) -> set[str]:
    tokens: set[str] = set()
    for segment in field_path.split("/"):
        if not segment:
            continue
        name = segment.replace("~1", "/").replace("~0", "~")
        name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()
        tokens.update(re.findall(r"[a-z0-9]+", name))
    return tokens


def _identifier_kind(field_path: str) -> str | None:
    tokens = _context_tokens(field_path)
    leaf = _leaf_name(field_path)
    id_like = bool(re.search(r"(?:^|_)(?:id|uuid|key|uri|url|path)$", leaf))
    if tokens & ACTOR_TOKENS:
        return "actor_identifier"
    if tokens & ARTIFACT_TOKENS and (id_like or tokens & {"file", "repo", "repository", "branch"}):
        return "artifact_identifier"
    if tokens & {"artifact", "url", "uri"}:
        return "artifact_identifier"
    return None


def _is_timestamp_field(field_path: str) -> bool:
    tokens = _context_tokens(field_path)
    leaf = _leaf_name(field_path)
    return bool(tokens & TIMESTAMP_TOKENS) or bool(
        re.search(r"(?:^|_)(?:created|updated|modified|started|ended)_at$", leaf)
    )


def _is_content_field(field_path: str) -> bool:
    return bool(_tokens(field_path) & CONTENT_TOKENS)


def _is_link_field(field_path: str) -> bool:
    tokens = _context_tokens(field_path)
    leaf = _leaf_name(field_path)
    return bool(tokens & LINK_TOKENS) and (
        leaf.endswith(("_id", "_ref", "_url", "_uri", "_path", "_key"))
        or bool(tokens & {"parent", "reply", "source", "target", "previous", "prev", "next", "ref"})
    )


def _is_boundary_field(field_path: str) -> bool:
    return bool(_context_tokens(field_path) & BOUNDARY_TOKENS)


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return "unknown"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _parse_timestamp(value: Any) -> tuple[datetime, str] | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            return None
        number = float(value)
        if 100_000_000 <= abs(number) < 10_000_000_000:
            unit = "epoch_seconds"
            seconds = number
        elif 100_000_000_000 <= abs(number) < 10_000_000_000_000:
            unit = "epoch_milliseconds"
            seconds = number / 1000
        else:
            return None
        try:
            return datetime.fromtimestamp(seconds, UTC), unit
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}(?:$|[T ])", text):
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")), "iso8601"
    except ValueError:
        return None


def _timestamp_display(value: datetime, aware: bool) -> str:
    if aware:
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return value.isoformat()


def _update_timestamp(stats: dict[str, Any], value: Any) -> None:
    if value is None:
        return
    parsed = _parse_timestamp(value)
    if parsed is None:
        stats["invalid_records"] += 1
        return
    timestamp, unit = parsed
    stats["parseable_records"] += 1
    stats["formats"][unit] += 1
    aware = timestamp.utcoffset() is not None
    key = "aware" if aware else "naive"
    stats[f"timezone_{key}_records"] += 1
    bucket = stats[key]
    if aware:
        timestamp = timestamp.astimezone(UTC)
    if bucket["minimum"] is None or timestamp < bucket["minimum"]:
        bucket["minimum"] = timestamp
    if bucket["maximum"] is None or timestamp > bucket["maximum"]:
        bucket["maximum"] = timestamp


def _timestamp_stats(fields: dict[str, dict[str, Any]], raw: dict[str, Any], total: int) -> list[dict[str, Any]]:
    result = []
    for field_path in sorted(raw):
        item = raw[field_path]
        field = fields[field_path]
        result.append(
            {
                "path": field_path,
                "present_records": field["present_records"],
                "missing_records": total - field["present_records"],
                "null_records": field["null_records"],
                "parseable_records": item["parseable_records"],
                "invalid_records": item["invalid_records"],
                "timezone_aware_records": item["timezone_aware_records"],
                "timezone_naive_records": item["timezone_naive_records"],
                "formats": dict(sorted(item["formats"].items())),
                "aware_range_utc": {
                    "minimum": _timestamp_display(item["aware"]["minimum"], True)
                    if item["aware"]["minimum"]
                    else None,
                    "maximum": _timestamp_display(item["aware"]["maximum"], True)
                    if item["aware"]["maximum"]
                    else None,
                },
                "naive_range_local": {
                    "minimum": _timestamp_display(item["naive"]["minimum"], False)
                    if item["naive"]["minimum"]
                    else None,
                    "maximum": _timestamp_display(item["naive"]["maximum"], False)
                    if item["naive"]["maximum"]
                    else None,
                },
            }
        )
    return result


def _timestamp_accumulator() -> dict[str, Any]:
    return {
        "parseable_records": 0,
        "invalid_records": 0,
        "timezone_aware_records": 0,
        "timezone_naive_records": 0,
        "formats": Counter(),
        "aware": {"minimum": None, "maximum": None},
        "naive": {"minimum": None, "maximum": None},
    }


def _file_format(path: Path) -> tuple[str, bool] | None:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if not suffixes:
        return None
    compressed = bool(suffixes and suffixes[-1] == ".gz")
    suffix = suffixes[-2] if compressed and len(suffixes) >= 2 else suffixes[-1]
    if suffix == ".jsonl":
        return "jsonl", compressed
    if suffix == ".ndjson":
        return "ndjson", compressed
    if suffix == ".csv":
        return "csv", compressed
    return None


def _raise_walk_error(error: OSError) -> None:
    raise InventoryError("input", "directory scan failed") from None


def _sources(input_path: Path) -> tuple[list[tuple[Path, str, bool, str]], Counter[str]]:
    if input_path.is_file():
        file_type = _file_format(input_path)
        if file_type is None:
            raise InventoryError(input_path.name, "unsupported file format")
        return [(input_path, file_type[0], file_type[1], input_path.name)], Counter()

    supported: list[tuple[Path, str, bool, str]] = []
    ignored_extensions: Counter[str] = Counter()
    for root, directories, filenames in os.walk(
        input_path, followlinks=False, onerror=_raise_walk_error
    ):
        directories[:] = sorted(name for name in directories if not (Path(root) / name).is_symlink())
        for name in sorted(filenames):
            path = Path(root) / name
            file_type = _file_format(path)
            if file_type is None:
                extension = path.suffix.lower() or "<none>"
                ignored_extensions[extension] += 1
                continue
            supported.append(
                (path, file_type[0], file_type[1], path.relative_to(input_path).as_posix())
            )
    supported.sort(key=lambda source: source[3])
    return supported, ignored_extensions


def _open_text(path: Path, compressed: bool) -> TextIO:
    if compressed:
        return gzip.open(path, "rt", encoding="utf-8-sig", newline="")
    return path.open("rt", encoding="utf-8-sig", newline="")


def _iter_jsonl(path: Path, compressed: bool, source: str, info: dict[str, Any]) -> Iterator[tuple[dict[str, Any], int]]:
    with _open_text(path, compressed) as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                info["blank_lines"] += 1
                continue
            try:
                record = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                raise InventoryError(source, "malformed JSON", line_number) from None
            if not isinstance(record, dict):
                raise InventoryError(source, "record MUST be a JSON object", line_number)
            yield record, line_number


def _iter_csv(path: Path, compressed: bool, source: str) -> Iterator[tuple[dict[str, Any], int]]:
    with _open_text(path, compressed) as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames
        if headers is None:
            return
        if any(not header for header in headers):
            raise InventoryError(source, "CSV header MUST NOT be empty")
        if len(set(headers)) != len(headers):
            raise InventoryError(source, "CSV headers MUST be unique")
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise InventoryError(source, "CSV row has more values than its header", row_number)
            yield dict(row), row_number


def _field_stats() -> dict[str, Any]:
    return {
        "present_records": 0,
        "null_records": 0,
        "empty_string_records": 0,
        "blank_string_records": 0,
        "types": Counter(),
        "string_records": 0,
        "string_length_minimum": None,
        "string_length_maximum": None,
        "string_length_total": 0,
    }


def _update_field(stats: dict[str, Any], value: Any) -> None:
    stats["present_records"] += 1
    stats["types"][_type_name(value)] += 1
    if value is None:
        stats["null_records"] += 1
    if isinstance(value, str):
        length = len(value)
        stats["string_records"] += 1
        stats["string_length_total"] += length
        current_min = stats["string_length_minimum"]
        current_max = stats["string_length_maximum"]
        stats["string_length_minimum"] = length if current_min is None else min(current_min, length)
        stats["string_length_maximum"] = length if current_max is None else max(current_max, length)
        if value == "":
            stats["empty_string_records"] += 1
        if not value.strip():
            stats["blank_string_records"] += 1


def _serializable_fields(raw: dict[str, dict[str, Any]], total: int) -> list[dict[str, Any]]:
    fields = []
    for field_path in sorted(raw):
        item = raw[field_path]
        string_lengths = None
        if item["string_records"]:
            string_lengths = {
                "records": item["string_records"],
                "minimum": item["string_length_minimum"],
                "maximum": item["string_length_maximum"],
                "mean": round(item["string_length_total"] / item["string_records"], 2),
            }
        fields.append(
            {
                "path": field_path,
                "present_records": item["present_records"],
                "missing_records": total - item["present_records"],
                "null_records": item["null_records"],
                "empty_string_records": item["empty_string_records"],
                "blank_string_records": item["blank_string_records"],
                "types": dict(sorted(item["types"].items())),
                "string_lengths": string_lengths,
            }
        )
    return fields


def _value_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _candidate_fields(
    field_stats: dict[str, dict[str, Any]], unique_values: dict[str, int], total: int
) -> list[dict[str, Any]]:
    result = []
    for field_path, field in field_stats.items():
        kind = _identifier_kind(field_path)
        if kind is None:
            continue
        leaf = _leaf_name(field_path)
        id_like = bool(re.search(r"(?:^|_)(?:id|uuid|key|uri|url|path)$", leaf))
        result.append(
            {
                "path": field_path,
                "kind": kind,
                "confidence": "medium" if id_like else "low",
                "present_records": field["present_records"],
                "missing_records": total - field["present_records"],
                "non_null_records": field["present_records"] - field["null_records"],
                "distinct_non_null_values": unique_values.get(field_path, 0),
                "interpretation": "Field-name candidate only; this does not establish a stable identity.",
            }
        )
    return sorted(result, key=lambda item: item["path"])


def _field_path_lists(field_stats: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    paths = sorted(field_stats)
    return {
        "content_fields": [path for path in paths if _is_content_field(path)],
        "possible_link_fields": [path for path in paths if _is_link_field(path)],
        "boundary_fields": [path for path in paths if _is_boundary_field(path)],
        "lineage_marker_fields": [
            path for path in paths if _context_tokens(path) & LINEAGE_TOKENS
        ],
    }


def _unit_assessment(field_stats: dict[str, dict[str, Any]]) -> dict[str, Any]:
    paths = sorted(field_stats)
    event_fields = [path for path in paths if _context_tokens(path) & EVENT_TOKENS]
    snapshot_fields = [path for path in paths if _context_tokens(path) & SNAPSHOT_TOKENS]
    if event_fields and snapshot_fields:
        hypothesis = "mixed_signals"
    elif event_fields:
        hypothesis = "event_like"
    elif snapshot_fields:
        hypothesis = "snapshot_like"
    else:
        hypothesis = "unknown"
    return {
        "hypothesis": hypothesis,
        "confidence": "low" if event_fields or snapshot_fields else "none",
        "event_marker_fields": event_fields,
        "snapshot_marker_fields": snapshot_fields,
        "basis": "Field names only. This does not classify individual records or establish event semantics.",
    }


def inventory_dataset(input_path: Path | str) -> dict[str, Any]:
    """Stream supported records and return a value-free dataset inventory.

    Supported sources are JSONL, NDJSON, and CSV, with optional gzip compression.
    A directory scan includes supported files recursively and ignores other files.
    """
    try:
        resolved = Path(input_path).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        raise InventoryError("input", "path does not exist or cannot be resolved") from None
    if not resolved.is_file() and not resolved.is_dir():
        raise InventoryError("input", "path MUST be a file or directory")

    sources, ignored_extensions = _sources(resolved)
    if not sources:
        raise InventoryError("input", "no supported JSONL, NDJSON, or CSV files found")

    field_stats: dict[str, dict[str, Any]] = {}
    timestamp_stats: dict[str, dict[str, Any]] = {}
    file_reports: list[dict[str, Any]] = []
    format_files: Counter[str] = Counter()
    total_records = 0
    blank_lines = 0

    with tempfile.TemporaryDirectory(prefix="dataset-morphology-") as temporary_directory:
        connection = sqlite3.connect(Path(temporary_directory) / "hashes.sqlite")
        try:
            connection.execute("PRAGMA journal_mode=OFF")
            connection.execute("PRAGMA synchronous=OFF")
            connection.execute("CREATE TABLE record_hashes (digest TEXT PRIMARY KEY)")
            connection.execute(
                "CREATE TABLE field_values (field_path TEXT, digest TEXT, PRIMARY KEY(field_path, digest))"
            )
            for path, file_format, compressed, source in sources:
                info: dict[str, Any] = {"blank_lines": 0}
                count = 0
                format_files[file_format] += 1
                try:
                    if file_format in {"jsonl", "ndjson"}:
                        records = _iter_jsonl(path, compressed, source, info)
                    else:
                        records = _iter_csv(path, compressed, source)
                    for record, row_number in records:
                        try:
                            serialized = _canonical_json(record)
                        except (TypeError, ValueError):
                            raise InventoryError(source, "record cannot be represented as strict JSON", row_number) from None
                        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
                        connection.execute("INSERT OR IGNORE INTO record_hashes VALUES (?)", (digest,))
                        for field_path, value in _flatten(record):
                            stats = field_stats.setdefault(field_path, _field_stats())
                            _update_field(stats, value)
                            if _is_timestamp_field(field_path) and field_path not in timestamp_stats:
                                timestamp_stats[field_path] = _timestamp_accumulator()
                            if _is_timestamp_field(field_path):
                                _update_timestamp(timestamp_stats[field_path], value)
                            if _identifier_kind(field_path) and value is not None and not isinstance(
                                value, (dict, list)
                            ):
                                value_hash = _value_digest(value)
                                connection.execute(
                                    "INSERT OR IGNORE INTO field_values VALUES (?, ?)",
                                    (field_path, value_hash),
                                )
                        count += 1
                        total_records += 1
                except InventoryError:
                    raise
                except (OSError, EOFError, UnicodeDecodeError, csv.Error, zlib.error):
                    raise InventoryError(source, "source is damaged or unreadable") from None
                blank_lines += info["blank_lines"]
                file_reports.append(
                    {
                        "path": source,
                        "format": file_format,
                        "compressed": compressed,
                        "size_bytes": path.stat().st_size,
                        "record_count": count,
                        "blank_lines": info["blank_lines"],
                    }
                )
            connection.commit()
            unique_records = connection.execute("SELECT COUNT(*) FROM record_hashes").fetchone()[0]
            unique_values = dict(
                connection.execute(
                    "SELECT field_path, COUNT(*) FROM field_values GROUP BY field_path"
                ).fetchall()
            )
        finally:
            connection.close()

    fields = _serializable_fields(field_stats, total_records)
    candidate_fields = _candidate_fields(field_stats, unique_values, total_records)
    paths = _field_path_lists(field_stats)
    return {
        "schema_version": 1,
        "input": {
            "kind": "file" if resolved.is_file() else "directory",
            "name": resolved.name,
            "supported_formats": ["jsonl", "ndjson", "csv", "gzip-compressed variants"],
            "ignored_file_count": sum(ignored_extensions.values()),
            "ignored_extensions": dict(sorted(ignored_extensions.items())),
        },
        "dataset": {
            "record_count": total_records,
            "source_file_count": len(file_reports),
            "format_file_counts": dict(sorted(format_files.items())),
            "blank_jsonl_lines": blank_lines,
        },
        "sources": file_reports,
        "fields": fields,
        "candidate_fields": candidate_fields,
        "timestamps": _timestamp_stats(field_stats, timestamp_stats, total_records),
        "content_fields": paths["content_fields"],
        "possible_link_fields": paths["possible_link_fields"],
        "boundary_fields": paths["boundary_fields"],
        "duplicates": {
            "exact_duplicate_records": total_records - unique_records,
            "unique_record_count": unique_records,
            "basis": "Canonical JSON record equality; this does not identify derived records.",
        },
        "derived_data_assessment": {
            "status": "not_inferred",
            "lineage_marker_fields": paths["lineage_marker_fields"],
            "basis": "Field names and exact duplicates do not establish derivation or cumulative state.",
        },
        "unit_assessment": _unit_assessment(field_stats),
        "assumptions": [
            "Each JSONL or NDJSON object line and each CSV data row is one observable record.",
            "Nested JSON objects use JSON Pointer paths. Arrays remain atomic fields.",
            "Candidate identifiers come from field names and do not establish actor identity.",
            "Timestamp parsing accepts ISO-8601 dates and times plus epoch seconds or milliseconds.",
            "Naive timestamps remain timezone-unknown and are not converted to UTC.",
            "Unit labels are low-confidence field-name hypotheses, not record classifications.",
            "The inventory reports no source text or identifier values.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect JSONL, NDJSON, or CSV records without emitting source values."
    )
    parser.add_argument("input", type=Path, help="a JSONL, NDJSON, CSV file, or directory")
    parser.add_argument("--output", type=Path, help="write the JSON report to this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = inventory_dataset(args.input)
        output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            sys.stdout.write(output)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
    except (InventoryError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
