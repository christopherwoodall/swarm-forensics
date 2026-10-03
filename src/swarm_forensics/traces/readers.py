"""Streaming normalizers for the three external trace reservoirs.

Each reader streams its archive one line at a time and yields normalized event
rows. The readers MUST NOT load a complete archive into memory. Field values are
copied from the source records; normalized fields are derived only from values
present in the record. Where a value is an analyst inference, it goes to notes.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import re
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

RELAY_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?"
    r"(markdown\.new|r\.jina\.ai|allorigins\.hexlet\.app|api\.allorigins\.win|"
    r"cors\.bwa\.workers\.dev|proxymule\.com|pure\.md|jqp\.vercel\.app|"
    r"md\.succ\.ai|html\.cafe|jsonhero\.io|r-jina-ai\.translate\.goog|"
    r"markdown-new\.translate\.goog)/"
)
HTTPBIN_PATTERN = re.compile(r"httpbin\.org")
ZZ_PATTERN = re.compile(r"zz=([0-9A-Za-z]+)")
EPOCH_NAME_PATTERN = re.compile(r"(17[89]\d{8})")
SHORTENER_HOSTS = (
    "rmn.re",
    "is.gd",
    "v.gd",
    "da.gd",
    "tinyurl.com",
    "uoft.me",
    "goto.unm.edu",
    "u.ethz.ch",
    "url.popcat.xyz",
    "vanderbi.lt",
)
AGENT_LABEL_PATTERN = re.compile(
    r"^(?:Agent|OpenAI|Data|Research|Diligent|Archive|Cashier)[A-Za-z0-9_]*$"
)
INVESTIGATOR_LABELS = {"ResearchUser", "ResearchQux", "ResearchTesterX", "ResearchOur"}


def _num(value: str) -> str:
    return value.strip() if isinstance(value, str) else ""


def technique_family_for(url: str) -> str:
    """Classify one URL into a technique family using visible structure only."""
    if RELAY_PATTERN.search(url):
        return "relay_fetch"
    if HTTPBIN_PATTERN.search(url):
        return "relay_indirection"
    if SHORTENER_HOSTS and any(h in url for h in SHORTENER_HOSTS):
        return "shortener_c2"
    return "unknown"


def actor_hint_for_label(label: str) -> str:
    """Map a wiki label to an actor hint using the investigation's caution."""
    if not label:
        return "unattributed"
    if label in INVESTIGATOR_LABELS:
        return "investigator"
    if AGENT_LABEL_PATTERN.match(label):
        return "agent_label"
    return "unattributed"


def relay_url_only(url: str) -> bool:
    return technique_family_for(url) != "unknown"


def _added_text(rev: dict[str, Any]) -> str:
    lines = (rev.get("body") or "").splitlines()
    parts: list[str] = []
    for hunk in rev.get("hunks") or []:
        if hunk.get("op") == "insert":
            parts.append("\n".join(lines[hunk["b0"]:hunk["b1"]]))
    return "\n".join(parts)


def iter_wiki_revisions(zip_path: Path) -> Iterator[dict[str, Any]]:
    """Stream wiki revisions from the full-wiki-logs.zip archive."""
    with zipfile.ZipFile(zip_path) as archive, archive.open("revisions.jsonl") as handle:
        for raw in handle:
            yield json.loads(raw)


def iter_wiki_events(zip_path: Path) -> Iterator[dict[str, Any]]:
    """Stream wiki events (save/delete/revert/probe) from the wiki archive."""
    with zipfile.ZipFile(zip_path) as archive, archive.open("events.jsonl") as handle:
        for raw in handle:
            yield json.loads(raw)


def iter_gem_records(records_path: Path) -> Iterator[dict[str, Any]]:
    """Stream rubygems-origin records from records.jsonl.gz."""
    with gzip.open(records_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            yield json.loads(line)


def iter_arquivo_captures(csv_path: str, archive: zipfile.ZipFile) -> Iterator[dict[str, Any]]:
    """Stream arquivo capture rows from one inside-zip CSV."""
    with archive.open(csv_path) as handle:
        yield from csv.DictReader(io.TextIOWrapper(handle, "utf-8"))


def parse_timestamp(value: str) -> str:
    """Normalize a timestamp to seconds precision; keep the source string on failure."""
    value = (value or "").strip()
    if not value:
        return ""
    match = re.match(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})", value)
    if match:
        return f"{match.group(1)}T{match.group(2)}Z"
    return value
