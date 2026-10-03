"""Arquivo reservoir normalizer.

Streams every arquivo-captures.csv inside the us-canada evidence zip. Each row
becomes one request event with the zz= nonce preserved when present. The
fresh-response layer (sources.csv) becomes read events where the investigation
itself re-fetched a capture: that layer is investigator-provenance.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from collections.abc import Iterator
from pathlib import Path

from swarm_forensics.traces.rows import mk_event, short

ZZ_PATTERN = re.compile(r"zz=([0-9A-Za-z]+)")
USCAN_BASE = "us-canada-government-evidence-2026-09-30-v3/"


def _rows(archive: zipfile.ZipFile, name: str) -> Iterator[dict[str, str]]:
    with archive.open(name) as handle:
        yield from csv.DictReader(io.TextIOWrapper(handle, "utf-8"))


def arquivo_event_rows(uscan_zip: Path) -> Iterator[dict[str, str]]:
    """Stream normalized event rows for the arquivo reservoir."""
    with zipfile.ZipFile(uscan_zip) as archive:
        names = sorted(n for n in archive.namelist() if n.endswith("arquivo-captures.csv"))
        for name in names:
            folder = name.split("/")[-2]
            for row in _rows(archive, name):
                url = row.get("target_url") or ""
                nonce = ZZ_PATTERN.search(url)
                notes = (
                    f"status={row.get('indexed_http_status')} "
                    f"mime={row.get('mime')} collection={row.get('collection')}"
                )
                if nonce:
                    notes += f" zz_nonce={nonce.group(1)}"
                yield mk_event(
                    eid=f"arquivo-{folder}-{row.get('record_number')}",
                    dataset="arquivo",
                    time=row.get("captured_at_utc") or "",
                    actor_hint="unattributed",
                    action="request",
                    target=url[:200],
                    artifact="",
                    operation="archive_capture",
                    technique_family="nonce_grammar" if nonce else "unknown",
                    raw_ref=(
                        f"{USCAN_BASE}{folder}/arquivo-captures.csv:"
                        f"record_number={row.get('record_number')}"
                    ),
                    notes=short(notes, 280),
                )


def uscan_response_rows(uscan_zip: Path) -> Iterator[dict[str, str]]:
    """Stream read events for the investigation's fresh-response layer."""
    with zipfile.ZipFile(uscan_zip) as archive:
        names = sorted(n for n in archive.namelist() if n.endswith("sources.csv"))
        for name in names:
            folder = name.split("/")[-2]
            for row in _rows(archive, name):
                source = row.get("source_url") or ""
                if not source:
                    continue
                yield mk_event(
                    eid=f"uscan-read-{folder}-{hash_source(source)}",
                    dataset="arquivo",
                    time=row.get("captured_at_utc") or "",
                    actor_hint="investigator",
                    action="read",
                    target=source[:200],
                    artifact=f"response:{row.get('file')}",
                    operation="fresh_response_read",
                    technique_family="unknown",
                    raw_ref=f"{USCAN_BASE}{folder}/sources.csv:file={row.get('file')}",
                    notes=short(
                        f"http_status={row.get('http_status')} "
                        f"source_sha256_prefix={row.get('source_sha256','')[:12]}"
                    ),
                )


def hash_source(source: str) -> str:
    import hashlib

    return hashlib.sha256(source.encode("utf-8", "replace")).hexdigest()[:12]
