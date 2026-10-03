"""RubyGems and URLQuery reservoir normalizers.

rubygems: registry_metadata records become register events (package
publication), package_member records become publish events. homepage_uri
sha256 values are preserved in notes: they are the exact-URL overlap key
against the wiki links corpus.

urlquery: the catalog rows become request events. The catalog carries no
request bodies, so each row's evidence level is a report link plus metadata;
the report-level HTTP exports inside the us-can package carry the bodies.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from swarm_forensics.traces.readers import iter_gem_records
from swarm_forensics.traces.rows import mk_event, short

UQ_BASE = "urlquery-agent-activity-2026-09-22-v5/"
SHA_IN_URL = re.compile(r"sha256=([0-9a-f]{64})")


def gem_event_rows(records_gz: Path) -> Iterator[dict[str, str]]:
    """Stream normalized register/publish events for rubygems-origin records."""
    for record in iter_gem_records(records_gz):
        for origin in record.get("origins", []):
            if origin.get("site") != "rubygems.org":
                continue
            kind = origin.get("kind") or ""
            text = record.get("text") or ""
            if kind == "registry_metadata":
                info: dict[str, Any] = {}
                try:
                    info = json.loads(text)
                except ValueError:
                    info = {}
                name = info.get("name") or ""
                homepage = info.get("homepage_uri") or ""
                shas = SHA_IN_URL.findall(homepage)
                notes = f"homepage_host_sha={[s[:12] for s in shas]}"
                if info.get("version"):
                    notes += f" version={info.get('version')}"
                yield mk_event(
                    eid=f"gem-reg-{hash_id(record['id'])}",
                    dataset="rubygems",
                    time=origin.get("source_date_literal") or "",
                    actor_hint="unattributed",
                    action="register",
                    target=f"rubygems:{name}",
                    artifact=f"package:{name}",
                    operation="registry_metadata",
                    technique_family="registry_abuse",
                    raw_ref=f"records.jsonl.gz!{record['id']}",
                    notes=short(notes, 280),
                    time_grade="registry_metadata_date",
                )
            elif kind == "package_member":
                yield mk_event(
                    eid=f"gem-member-{hash_id(record['id'])}",
                    dataset="rubygems",
                    time=origin.get("source_date_literal") or "",
                    actor_hint="unattributed",
                    action="publish",
                    target="rubygems",
                    artifact=f"package_member:{hash_id(record['id'])}",
                    operation="package_member",
                    technique_family="registry_abuse",
                    raw_ref=f"records.jsonl.gz!{record['id']}",
                    notes=short(text, 200),
                    time_grade="unknown_date",
                )


def urlquery_event_rows(uq_zip: Path) -> Iterator[dict[str, str]]:
    """Stream normalized request events from the urlquery catalog."""
    with zipfile.ZipFile(uq_zip) as archive:
        for row in _csv_rows(archive, f"{UQ_BASE}all-reports.csv"):
            disposition = row.get("disposition") or ""
            if disposition != "included":
                continue
            yield mk_event(
                eid=f"uq-{row['report_id']}",
                dataset="urlquery",
                time=row.get("report_date_utc") or "",
                actor_hint="unattributed",
                action="request",
                target=f"report:{row['report_id']}",
                artifact="",
                operation="browser_session_report",
                technique_family="unknown",
                raw_ref=f"urlquery-agent-activity-2026-09-22-v5/all-reports.csv:report_id={row['report_id']}",
                notes=short(
                    f"confidence={row.get('confidence')} broad_class={row.get('broad_class')} "
                    f"precision={row.get('timestamp_precision')}"
                ),
                time_grade="report_timestamp_second_precision",
            )


def urlquery_http_rows(uscan_zip: Path) -> Iterator[dict[str, str]]:
    """Stream request events from the report-level HTTP exports."""
    import zipfile as zf

    base = "us-canada-government-evidence-2026-09-30-v3/"
    with zf.ZipFile(uscan_zip) as archive:
        names = sorted(n for n in archive.namelist() if n.endswith("urlquery-http.csv"))
        for name in names:
            folder = name.split("/")[-2]
            with archive.open(name) as handle:
                for row in csv.DictReader(io.TextIOWrapper(handle, "utf-8")):
                    url = row.get("url") or ""
                    yield mk_event(
                        eid=(
                            f"uq-http-{folder}-{row['report_id'][:8]}-"
                            f"{row.get('http_entry_index')}"
                        ),
                        dataset="urlquery",
                        time=row.get("request_at_utc") or "",
                        actor_hint="unattributed",
                        action="request",
                        target=url[:200],
                        artifact="",
                        operation="http_entry",
                        technique_family=_family(url),
                        raw_ref=(
                            f"{base}{folder}/urlquery-http.csv:"
                            f"report_id={row.get('report_id')} entry={row.get('http_entry_index')}"
                        ),
                        notes=short(
                            f"status={row.get('http_status')} "
                            f"peer={row.get('remote_peer_ip')} body_saved={row.get('response_body_in_source_json')}"
                        ),
                    )


def _family(url: str) -> str:
    from swarm_forensics.traces.readers import technique_family_for

    return technique_family_for(url)


def _csv_rows(archive: zipfile.ZipFile, name: str) -> Iterator[dict[str, str]]:
    with archive.open(name) as handle:
        yield from csv.DictReader(io.TextIOWrapper(handle, "utf-8"))


def hash_id(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
