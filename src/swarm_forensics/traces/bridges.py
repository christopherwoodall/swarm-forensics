"""Cross-dataset bridge detection and overlap probing.

Stage 1 hunts are per-reservoir. This module implements the stage-2 question:
repeated mechanisms, literals, target sets, artifact names, and request
grammars that could link episodes across substrates. Every bridge candidate
keeps identity linkage, common harness, common task, common operator, and
direct transfer as separate hypotheses.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterator
from pathlib import Path

from swarm_forensics.traces.rows import mk_edge

SOURCES = Path("colette-research/sources")
SHA_IN_URL = re.compile(r"sha256=([0-9a-f]{64})")
UQ_REPORT_IN_TEXT = re.compile(r"urlquery\.net/report/([0-9a-f-]{36})")
RELAY_HOSTS = (
    "markdown.new",
    "r.jina.ai",
    "allorigins.hexlet.app",
    "api.allorigins.win",
    "cors.bwa.workers.dev",
    "proxymule.com",
    "pure.md",
    "jqp.vercel.app",
    "md.succ.ai",
    "html.cafe",
    "jsonhero.io",
)
TRANSFER_WORDS = ("transmit", "transfer", "handoff")


def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


def collect_wiki_added_text(zip_path: Path) -> Iterator[tuple[str, str, str]]:
    """Yield (rev_id, time, added_text) for every wiki revision."""
    with zipfile.ZipFile(zip_path) as archive, archive.open("revisions.jsonl") as handle:
        for raw in handle:
            rev = json.loads(raw)
            lines = (rev.get("body") or "").splitlines()
            parts = []
            for hunk in rev.get("hunks") or []:
                if hunk.get("op") == "insert":
                    parts.append("\n".join(lines[hunk["b0"]:hunk["b1"]]))
            yield rev["rev_id"], rev.get("time") or "", "\n".join(parts)


def gem_homepage_shas(records_gz: Path) -> dict[str, str]:
    """Map gem homepage sha256 -> package name."""
    mapping: dict[str, str] = {}
    with gzip.open(records_gz, "rt", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            for origin in record.get("origins", []):
                if origin.get("site") != "rubygems.org" or origin.get("kind") != "registry_metadata":
                    continue
                try:
                    info = json.loads(record.get("text") or "{}")
                except ValueError:
                    continue
                for sha in SHA_IN_URL.findall(info.get("homepage_uri") or ""):
                    mapping[sha] = info.get("name") or record["id"]
    return mapping


def wiki_link_shas(links_gz: Path) -> dict[str, list[str]]:
    """Map link sha256 -> record ids citing that URL."""
    by_sha: dict[str, list[str]] = defaultdict(list)
    with gzip.open(links_gz, "rt", encoding="utf-8") as handle:
        for line in handle:
            link = json.loads(line)
            sha = link.get("source_url_sha256")
            if sha:
                by_sha[sha].extend(link.get("record_ids", []))
    return by_sha


def gem_wiki_overlap_edges(
    records_gz: Path, links_gz: Path
) -> Iterator[dict[str, str]]:
    """The radioactive marble probe: exact URL overlap between gem homepages and wiki links."""
    gem = gem_homepage_shas(records_gz)
    wiki = wiki_link_shas(links_gz)
    for sha in sorted(set(gem) & set(wiki)):
        pkg = gem[sha]
        citing = wiki[sha]
        yield mk_edge(
            eid=f"edge-gemwiki-{sha[:16]}",
            edge_from=f"rubygems:package:{pkg}",
            edge_to=f"wiki:links:{sha[:16]}",
            relation="exact_url_overlap",
            evidence_type="identical_sha256_of_operational_url",
            causal_strength="resemblance_only",
            competing=(
                "common upstream task structure; independent rediscovery; "
                "shared scaffolding; artifact-mediated inheritance"
            ),
            raw_ref=(
                f"records.jsonl.gz homepage_uri sha256={sha}; "
                f"links.jsonl.gz source_url_sha256={sha} record_ids={len(citing)}"
            ),
            notes=(
                "exact URL overlap only; neither retrieval by the other side nor "
                "behavioral dependence is established"
            ),
        )


def urlquery_citation_edges(wiki_zip: Path, uq_zip: Path) -> Iterator[dict[str, str]]:
    """Wiki revisions whose added text cites a urlquery report."""
    import csv
    import io

    uq_base = "urlquery-agent-activity-2026-09-22-v5/"
    catalog: set[str] = set()
    with zipfile.ZipFile(uq_zip) as archive, archive.open(f"{uq_base}all-reports.csv") as handle:
        for row in csv.DictReader(io.TextIOWrapper(handle, "utf-8")):
            catalog.add(row["report_id"])

    for rev_id, time, added in collect_wiki_added_text(wiki_zip):
        for report in UQ_REPORT_IN_TEXT.findall(added):
            in_catalog = report in catalog
            yield mk_edge(
                eid=f"edge-wikiuq-{hashlib.sha1(rev_id.encode()).hexdigest()[:10]}",
                edge_from=f"wiki:rev:{rev_id}",
                edge_to=f"urlquery:report:{report}",
                relation="cites_report",
                evidence_type="added_text_citation",
                causal_strength="temporal_structural_association_only",
                competing=(
                    "investigator provenance; agent found report independently; "
                    "agent produced the cited session"
                ),
                raw_ref=f"full-wiki-logs.zip!revisions.jsonl:{rev_id} added text; catalog match={in_catalog}",
                notes=f"citation time={time} catalog_match={in_catalog}",
            )
        del time
    return


def shared_relay_edges(records_gz: Path, links_gz: Path) -> Iterator[dict[str, str]]:
    """Shared relay hosts across datasets, counted from grounded values only.

    rubygems side: relay hosts named inside gem homepage_uri strings.
    wiki side: relay hosts named inside wiki link rows (url field carries the
    host when the exact URL is withheld).
    """
    import gzip
    import json

    gem_hosts: Counter = Counter()
    with gzip.open(records_gz, "rt", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            for origin in record.get("origins", []):
                if origin.get("site") != "rubygems.org":
                    continue
                text = record.get("text") or ""
                for host in RELAY_HOSTS:
                    if host in text:
                        gem_hosts[host] += 1
    wiki_hosts: Counter = Counter()
    with gzip.open(links_gz, "rt", encoding="utf-8") as handle:
        for line in handle:
            link = json.loads(line)
            url = link.get("url") or ""
            for host in RELAY_HOSTS:
                if host in url:
                    wiki_hosts[host] += 1
    for host in RELAY_HOSTS:
        if gem_hosts[host] == 0 and wiki_hosts[host] == 0:
            continue
        yield mk_edge(
            eid=f"edge-relay-{hashlib.sha256(host.encode()).hexdigest()[:12]}",
            edge_from="dataset:rubygems",
            edge_to="dataset:wiki",
            relation="shared_relay_host",
            evidence_type="host_name_in_both_corpora",
            causal_strength="resemblance_only",
            competing="common harness; common task; shared scaffolding; common operator",
            raw_ref=(
                f"rubygems records mentioning {host}: {gem_hosts[host]}; "
                f"wiki links mentioning {host}: {wiki_hosts[host]}"
            ),
            notes="same relay service named in both populations; no transmission established",
        )
