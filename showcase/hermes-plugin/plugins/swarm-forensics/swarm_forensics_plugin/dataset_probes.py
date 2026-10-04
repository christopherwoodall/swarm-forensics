"""Stream operator-selected datasets and discover unnamed recorded sequences."""

import csv
import gzip
import hashlib
import heapq
import itertools
import json
import random
import sqlite3
import tempfile
from collections import Counter, deque
from datetime import datetime
from pathlib import Path

from .safety import fence_untrusted


class DatasetError(ValueError):
    """Refuse unsupported sources or invalid probe options."""


def digest(value):
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def field_value(record, pointer):
    if pointer is None:
        return None
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise DatasetError("Fields MUST use JSON Pointer paths.")
    value = record
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def fields(record, prefix=""):
    for name, value in record.items():
        pointer = prefix + "/" + name.replace("~", "~0").replace("/", "~1")
        if isinstance(value, dict):
            yield from fields(value, pointer)
        else:
            yield pointer, value


def _reject_constant(value):
    raise ValueError("Non-finite JSON number.")


def _csv_records(handle):
    """Preserve physical record-start lines, including multiline cells and blank lines."""
    reader = csv.DictReader(handle)
    names = reader.fieldnames
    if names is None:
        return
    while True:
        line = reader.reader.line_num + 1
        try:
            values = next(reader.reader)
        except StopIteration:
            return
        if not values:
            continue
        record: dict = dict(zip(names, values))
        if len(values) > len(names):
            record[reader.restkey] = values[len(names):]
        for name in names[len(values):]:
            record[name] = reader.restval
        yield line, record


def _scoped_rows(handle, extension, remaining):
    """Stop before parsing another record after the scope cap."""
    rows = _csv_records(handle) if extension == "csv" else enumerate(handle, 1)
    consumed = 0
    while True:
        if consumed == remaining:
            if any(line.strip() for line in handle):
                yield None, None
            return
        try:
            line, raw = next(rows)
        except StopIteration:
            return
        if isinstance(raw, str) and not raw.strip():
            continue
        consumed += 1
        yield line, raw


class DatasetProbes:
    """Keep raw values transient. Store only hashes, references, and derived ordering."""

    def __init__(self, path, *, content_field=None, actor_field=None, artifact_field=None,
                 operation_field=None, time_field=None, max_records=10000):
        try:
            self.path = Path(path).expanduser().resolve(strict=True)
        except OSError:
            raise DatasetError("Dataset path is unavailable.") from None
        if not isinstance(max_records, int) or isinstance(max_records, bool) \
                or not 1 <= max_records <= 1000000:
            raise DatasetError("max_records MUST be between 1 and 1000000.")
        self.max_records = max_records
        self.mapping = dict(content_field=content_field, actor_field=actor_field,
                            artifact_field=artifact_field, operation_field=operation_field,
                            time_field=time_field)
        for pointer in self.mapping.values():
            field_value({}, pointer)
        candidates = [self.path] if self.path.is_file() else sorted(self.path.rglob("*"))
        self.sources = []
        for source in candidates:
            if not source.is_file() or source.is_symlink():
                continue
            relative = source.name if self.path.is_file() else str(source.relative_to(self.path))
            if any(part.startswith(".") for part in Path(relative).parts):
                continue
            extension = source.name.removesuffix(".gz").rsplit(".", 1)[-1]
            if extension in ("jsonl", "ndjson", "csv"):
                self.sources.append((source, relative, extension))
        if not self.sources:
            raise DatasetError("Select JSONL, NDJSON, CSV, or gzip variants.")
        self.scope: dict = {"input_path_sha256": digest(str(self.path))}
        self.snapshot = {source: self._identity(source) for source, _, _ in self.sources}
        self.fingerprint = None

    @staticmethod
    def _identity(source):
        stat = source.stat()
        return stat.st_ino, stat.st_size, stat.st_mtime_ns

    def assert_unchanged(self):
        try:
            changed = any(self._identity(source) != identity
                          for source, identity in self.snapshot.items())
        except OSError:
            changed = True
        if changed:
            raise DatasetError("Dataset changed during discovery. Restart the run.")

    def _finish_scan(self, count, truncated, signature):
        self.assert_unchanged()
        fingerprint = signature.hexdigest()
        if self.fingerprint is not None and self.fingerprint != fingerprint:
            raise DatasetError("Dataset changed between scans. Restart the run.")
        self.fingerprint = fingerprint
        self.scope.update(record_count=count, truncated=truncated,
                          scanned_records_sha256=fingerprint)

    def records(self):
        self.assert_unchanged()
        count = 0
        signature = hashlib.sha256()
        for source, relative, extension in self.sources:
            opener = gzip.open if source.suffix == ".gz" else open
            try:
                with opener(source, "rt", encoding="utf-8", newline="") as handle:
                    remaining = self.max_records - count
                    for line, raw in _scoped_rows(handle, extension, remaining):
                        if line is None:
                            self._finish_scan(count, True, signature)
                            return
                        if isinstance(raw, str):
                            if not raw.strip():
                                continue
                            if len(raw) > 2000000:
                                raise DatasetError("Source record exceeds the size limit.")
                            try:
                                record = json.loads(raw, parse_constant=_reject_constant)
                            except ValueError:
                                raise DatasetError(f"Invalid JSON at {relative}#L{line}.") from None
                        else:
                            record = raw
                        if not isinstance(record, dict):
                            raise DatasetError(f"Object record required at {relative}#L{line}.")

                        count += 1
                        reference = f"{relative}#L{line}"
                        signature.update((reference + "\0" + digest(record) + "\n").encode())
                        yield reference, record
            except (OSError, EOFError, UnicodeError, csv.Error):
                raise DatasetError(f"Source is unreadable: {relative}.") from None
        self._finish_scan(count, False, signature)

    @staticmethod
    def _text_window(value, phrase, limit=1400):
        if not phrase:
            return value[:limit]
        folded = value.casefold()
        position = folded.find(phrase.casefold())
        if position < 0:
            return value[:limit]
        if len(folded) != len(value):
            offset = 0
            for index, character in enumerate(value):
                width = len(character.casefold())
                if offset + width > position:
                    position = index
                    break
                offset += width
        context = min(400, max(0, (limit - len(phrase.casefold())) // 2))
        start = max(0, position - context)
        return value[start:start + limit]

    def _preview(self, record, focus_phrase=None, focus_field=None):
        visible = {}
        selected = set(self.mapping.values())
        values = sorted(fields(record), key=lambda item: (
            not (focus_phrase and isinstance(item[1], str)
                 and (focus_field is None or item[0] == focus_field)
                 and focus_phrase.casefold() in item[1].casefold()),
            item[0] != self.mapping["content_field"], item[0] not in selected,
            -len(item[1]) if isinstance(item[1], str) else 0, item[0]))
        for pointer, value in values[:24]:
            key = pointer[1:]
            if len(key) > 200:
                continue
            if isinstance(value, str):
                original = value
                folded_phrase = (focus_phrase or "").casefold()
                focused = bool(folded_phrase and (focus_field is None or pointer == focus_field)
                               and folded_phrase in original.casefold())
                minimum = max(1, len(folded_phrase)) if focused else 1
                limit = 1400
                while True:
                    value = self._text_window(original, focus_phrase, limit)
                    candidate = json.dumps({**visible, key: value}, ensure_ascii=False)
                    if len(candidate) <= 1900:
                        break
                    if limit == minimum:
                        if focused:
                            raise DatasetError("Focused text cannot fit within the preview budget.")
                        break
                    limit = max(minimum, limit // 2)
            elif isinstance(value, list):
                value = {"array_items": len(value)}
            candidate = json.dumps({**visible, key: value}, ensure_ascii=False)
            if len(candidate) <= 1900:
                visible[key] = value
        return json.dumps(visible, ensure_ascii=False)

    def survey(self):
        """Inspect diverse records and mine repeated operation sequences without labels."""
        sample = []
        field_counts = Counter()
        with tempfile.TemporaryDirectory(prefix="sf-dataset-") as directory:
            with sqlite3.connect(Path(directory) / "hashes.sqlite") as conn:
                conn.execute("CREATE TABLE events(hash TEXT PRIMARY KEY, ref TEXT,"
                             " group_hash TEXT, actor_hash TEXT, op_hash TEXT,"
                             " stamp REAL, pos INT)")
                aware = 0
                operations = 0
                for position, (reference, record) in enumerate(self.records()):
                    record_hash = digest(record)
                    group = field_value(record, self.mapping["artifact_field"])
                    actor = field_value(record, self.mapping["actor_field"])
                    operation = field_value(record, self.mapping["operation_field"])
                    stamp = self._stamp(field_value(record, self.mapping["time_field"]))
                    inserted = conn.execute(
                        "INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?)",
                        (record_hash, reference, digest(group) if group is not None else None,
                         digest(actor) if actor is not None else None,
                         digest(operation) if operation is not None else None, stamp, position),
                    )
                    if not inserted.rowcount:
                        continue
                    field_counts.update(pointer for pointer, _ in fields(record))
                    if operation is not None and group is not None:
                        operations += 1
                        aware += stamp is not None
                    # Select a stable bounded sample across the scanned scope, not its first rows.
                    entry = (-int(record_hash, 16), reference, self._preview(record))
                    if len(sample) < 16:
                        heapq.heappush(sample, entry)
                    elif entry[0] > sample[0][0]:
                        heapq.heapreplace(sample, entry)
                unique = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                self.scope.update(unique_records=unique,
                                  exact_duplicates=self.scope["record_count"] - unique,
                                  source_files=len(self.sources),
                                  unit_basis="Selected field values, not verified agents.")
                ordering = ("aware_timestamp" if operations and aware == operations
                            else "source_order")
                sequences = self._sequences(conn, ordering) if operations else []
        return {
            "scope": dict(self.scope), "fields": dict(sorted(field_counts.items())),
            "samples": [{"source_ref": reference,
                         "record_untrusted": fence_untrusted(preview, "dataset record", 2000)}
                        for _, reference, preview in sorted(sample, reverse=True)],
            "sequences": sequences,
            "limitations": [
                "Sampling is descriptive, not representative or exhaustive.",
                "A prefix-limited scan cannot establish dataset-wide absence.",
                "Selected actor and artifact fields do not authenticate identities.",
                "Examples flatten nested keys, truncate text, and summarize arrays.",
            ],
        }

    @staticmethod
    def _stamp(value):
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.timestamp() if parsed.tzinfo is not None else None
        except (ValueError, OverflowError):
            return None

    def _sequences(self, conn, ordering):
        conn.execute("CREATE TABLE motifs(sig TEXT, group_hash TEXT, refs TEXT)")
        conn.execute("CREATE TABLE nulls(sig TEXT, trial INT)")
        order = "stamp, pos" if ordering == "aware_timestamp" else "pos"
        rows = conn.execute("SELECT group_hash, op_hash, ref FROM events WHERE"
                            " group_hash IS NOT NULL AND op_hash IS NOT NULL"
                            f" ORDER BY group_hash,{order}")
        size = 3
        skipped = 0
        for group_hash, grouped in itertools.groupby(rows, key=lambda row: row[0]):
            events = list(itertools.islice(grouped, 2049))
            if len(events) > 2048:
                skipped += 1
                continue
            window = deque(maxlen=size)
            for _, operation, reference in events:
                window.append((operation, reference))
                if len(window) != size:
                    continue
                signature = tuple(item[0] for item in window)
                conn.execute("INSERT INTO motifs VALUES (?,?,?)",
                             (json.dumps(signature), group_hash,
                              json.dumps([item[1] for item in window])))
            hashes = [event[1] for event in events]
            for trial in range(20):
                shuffled = list(hashes)
                random.Random(group_hash + str(trial)).shuffle(shuffled)
                for start in range(len(shuffled) - size + 1):
                    signature = tuple(shuffled[start:start + size])
                    conn.execute("INSERT INTO nulls VALUES (?,?)",
                                 (json.dumps(signature), trial))
        self.scope["oversized_sequence_groups_skipped"] = skipped
        aggregates = conn.execute(
            "SELECT sig, COUNT(*), COUNT(DISTINCT group_hash) FROM motifs GROUP BY sig"
            " HAVING COUNT(*) >= 2 ORDER BY COUNT(DISTINCT group_hash) DESC,"
            " COUNT(*) DESC, sig LIMIT 12",
        ).fetchall()
        needed = {operation for sig, _, _ in aggregates for operation in json.loads(sig)}
        aliases = {}
        for _, record in self.records():
            operation = field_value(record, self.mapping["operation_field"])
            if operation is not None and digest(operation) in needed:
                aliases[digest(operation)] = str(operation)[:200]
        result = []
        for signature, occurrences, groups in aggregates:
            hashes = json.loads(signature)
            references = []
            for (raw_refs,) in conn.execute("SELECT refs FROM motifs WHERE sig = ? LIMIT 8",
                                           (signature,)):
                references.extend(json.loads(raw_refs))
            trials = dict(conn.execute("SELECT trial, COUNT(*) FROM nulls WHERE sig = ?"
                                       " GROUP BY trial", (signature,)).fetchall())
            null_counts = [trials.get(trial, 0) for trial in range(20)]
            result.append({
                "observation_id": "sequence-" + digest([
                    hashes, self.mapping, ordering, self.scope["input_path_sha256"],
                    self.scope["scanned_records_sha256"],
                ])[:24],
                "kind": "sequence", "signature_sha256": digest(hashes),
                "field_mapping": dict(self.mapping), "scope": dict(self.scope),
                "signature_untrusted": fence_untrusted(
                    json.dumps([aliases.get(operation, "unavailable") for operation in hashes]),
                    "discovered operation sequence", 2000),
                "sequence_length": len(hashes), "occurrences": occurrences, "groups": groups,
                "source_refs": sorted(set(references)), "ordering_basis": ordering,
                "evidence_strength": "e1",
                "null_baseline": {"method": "20 deterministic within-group order shuffles",
                                  "mean_occurrences": sum(null_counts) / 20,
                                  "maximum_occurrences": max(null_counts)},
                "limitation": "Repeated recorded order, not causality or verified coordination.",
            })
        return result

    def inspect_text(self, phrase, content_field=None, *, limit=3, exclude_refs=()):
        """Expose transient matching records and searchable contrasts within the existing scope."""
        if not isinstance(phrase, str) or not 1 <= len(phrase.strip()) <= 200:
            raise DatasetError("A probe phrase MUST contain 1 to 200 characters.")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 4:
            raise DatasetError("Inspection limit MUST be between 1 and 4.")
        pointer = content_field or self.mapping["content_field"]
        field_value({}, pointer)
        counts = Counter()
        excluded = set(exclude_refs)
        samples = {(matched, visited): [] for matched in (True, False) for visited in (True, False)}
        with tempfile.TemporaryDirectory(prefix="sf-inspect-") as directory:
            with sqlite3.connect(Path(directory) / "hashes.sqlite") as conn:
                conn.execute("CREATE TABLE seen(hash TEXT PRIMARY KEY)")
                for reference, record in self.records():
                    record_hash = digest(record)
                    if not conn.execute("INSERT OR IGNORE INTO seen VALUES (?)",
                                        (record_hash,)).rowcount:
                        continue
                    values = ([field_value(record, pointer)] if pointer else
                              [value for _, value in fields(record) if isinstance(value, str)])
                    text_values = [value for value in values if isinstance(value, str)]
                    if not text_values:
                        counts["unavailable"] += 1
                        continue
                    matched = any(phrase.casefold() in value.casefold() for value in text_values)
                    counts[matched] += 1
                    heap = samples[matched, reference in excluded]
                    priority = -int(record_hash, 16)
                    if len(heap) < limit or priority > heap[0][0]:
                        preview = self._preview(record, phrase if matched else None, pointer)
                        entry = (priority, reference, preview)
                        if len(heap) < limit:
                            heapq.heappush(heap, entry)
                        else:
                            heapq.heapreplace(heap, entry)
                unique = conn.execute("SELECT COUNT(*) FROM seen").fetchone()[0]

        def records(matched):
            selected = sorted(samples[matched, False], reverse=True)
            selected.extend(sorted(samples[matched, True], reverse=True))
            return [{"source_ref": reference,
                     "record_untrusted": fence_untrusted(preview, "inspected dataset record", 2000)}
                    for _, reference, preview in selected[:limit]]

        return {
            "matching_records": records(True), "contrast_records": records(False),
            "matched_count": counts[True], "contrast_count": counts[False],
            "unavailable_text_records": counts["unavailable"], "unique_records": unique,
            "scope": dict(self.scope),
            "selection_basis": ("Prefer unviewed records, then stable hashes. "
                                "Samples are not representative."),
            "limitations": ["Examples show bounded windows, not complete source records.",
                            "Contrasts are literal nonmatches, not forensic disproof."],
        }

    def text_probe(self, phrase, content_field=None):
        """Measure a model-proposed phrase and retain nonmatching source references."""
        if not isinstance(phrase, str) or not 1 <= len(phrase.strip()) <= 200:
            raise DatasetError("A probe phrase MUST contain 1 to 200 characters.")
        pointer = content_field or self.mapping["content_field"]
        field_value({}, pointer)
        references, counterexamples = [], []
        actors, artifacts = set(), set()
        matches = 0
        searchable = 0
        with tempfile.TemporaryDirectory(prefix="sf-text-probe-") as directory:
            with sqlite3.connect(Path(directory) / "hashes.sqlite") as conn:
                conn.execute("CREATE TABLE seen(hash TEXT PRIMARY KEY)")
                for reference, record in self.records():
                    if not conn.execute("INSERT OR IGNORE INTO seen VALUES (?)",
                                        (digest(record),)).rowcount:
                        continue
                    values = [field_value(record, pointer)] if pointer else [
                        value for _, value in fields(record) if isinstance(value, str)]
                    text_values = [value for value in values if isinstance(value, str)]
                    if not text_values:
                        continue
                    searchable += 1
                    matched = any(phrase.casefold() in value.casefold() for value in text_values)
                    if matched:
                        matches += 1
                        if len(references) < 24:
                            references.append(reference)
                        selected_fields = (("actor_field", actors), ("artifact_field", artifacts))
                        for field, target in selected_fields:
                            value = field_value(record, self.mapping[field])
                            if value is not None:
                                target.add(digest(value))
                    elif len(counterexamples) < 8:
                        counterexamples.append(reference)
                unique = conn.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
        return {
            "observation_id": "text-" + digest([pointer, phrase.casefold()])[:24], "kind": "text",
            "content_field": pointer,
            "signature_sha256": digest([pointer, phrase.casefold()]),
            "signature_untrusted": fence_untrusted(phrase, "proposed phrase", 200),
            "occurrences": matches, "unique_records": unique,
            "searchable_records": searchable, "unavailable_text_records": unique - searchable,
            "distinct_actor_values": len(actors) if self.mapping["actor_field"] else None,
            "distinct_artifact_values": len(artifacts) if self.mapping["artifact_field"] else None,
            "source_refs": references, "nonmatching_source_refs": counterexamples,
            "scope": dict(self.scope), "evidence_strength": "e0",
            "limitation": "Literal resemblance, not transmission. Significance is untested.",
        }
