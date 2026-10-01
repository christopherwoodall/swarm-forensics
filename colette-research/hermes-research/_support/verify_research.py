#!/usr/bin/env python3
"""Audit this research collection locally; no network or extra packages.

This checks structure and excerpt provenance, not universal claim correctness.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
CITE = re.compile(r"\[(\d+)\]")
LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")
MD_LINK = re.compile(r"\[([^\]]*)\]\((?:[^()\s]|\([^()]*\))*\)")
MD_NOISE = re.compile(r"[*_`~]|\\(?=[^\w\s])")
CASE_HEADING = re.compile(r"^## Case ([OPD]\d+)\s", re.MULTILINE)
EXPECTED_DOCS = {
    "README.md", "01-definitions-and-characteristics.md",
    "02-online-cases-fox8-and-openai-may-2024.md",
    "03-online-cases-spamouflage-zero-zeno-storm2035.md",
    "04-physical-swarm-cases.md", "05-digital-agent-experiments.md",
    "06-detection-current-and-evaluated.md",
    "07-detection-proposals-and-frontiers.md",
    "08-implications-and-research-agenda.md", "09-source-guide.md",
}


def match_key(text: str) -> str:
    collapsed = MD_LINK.sub(r"\1", text)
    return " ".join(MD_NOISE.sub("", collapsed).split()).casefold()


def main() -> int:
    errors: list[str] = []
    ledger = json.loads((ROOT / "_support/citation-ledger.json").read_text())
    metadata = json.loads((ROOT / "_support/source-records.json").read_text())
    manifest = json.loads((ROOT / "_support/case-manifest.json").read_text())
    by_id = {source["id"]: source for source in ledger["sources"]}
    records = {source["id"]: source for source in metadata["sources"]}
    cited: set[int] = set()
    guide_ids: set[int] = set()
    cases: dict[str, str] = {}
    files = []
    checked_links = 0
    checked_quotes = 0
    actual_docs = {p.name for p in ROOT.glob("*.md")}
    if actual_docs != EXPECTED_DOCS:
        errors.append(f"Document inventory mismatch: {sorted(actual_docs ^ EXPECTED_DOCS)}")

    for path in sorted(ROOT.glob("*.md")):
        text = path.read_text()
        body, separator, block = text.partition("\n## Sources\n")
        ids = {int(value) for value in CITE.findall(body)}
        cited.update(ids)
        if path.name == "09-source-guide.md":
            guide_ids = ids
        listed = {int(sid): url for sid, url in re.findall(
            r"^\[(\d+)\]\s+(https?://\S+)", block, re.MULTILINE)}
        if ids and not separator:
            errors.append(f"{path.name}: no Sources section")
        if set(listed) != ids:
            errors.append(f"{path.name}: listed sources differ from cited IDs")
        for sid in ids:
            if sid not in by_id or listed.get(sid) != by_id[sid]["url"]:
                errors.append(f"{path.name}: invalid citation/URL [{sid}]")
        for target in LINK.findall(body):
            split = urlsplit(target)
            if split.scheme or split.netloc or not split.path:
                continue
            destination = (path.parent / unquote(split.path)).resolve()
            checked_links += 1
            if not destination.exists():
                errors.append(f"{path.name}: missing local link {target}")
            if not destination.is_relative_to(ROOT):
                errors.append(f"{path.name}: local link outside collection {target}")
        for case_id in CASE_HEADING.findall(body):
            if case_id in cases:
                errors.append(f"Duplicate case heading: {case_id}")
            cases[case_id] = path.name
        if re.search(r"\b(?:TODO|TBD|FIXME)\b|\[SKILL_PRUNED\]", body):
            errors.append(f"{path.name}: unresolved placeholder")
        files.append({"file": path.name, "bytes": path.stat().st_size,
                      "body_words": len(body.split()), "lines": len(text.splitlines()),
                      "cited_sources": len(ids)})

    if guide_ids != cited or set(records) != cited:
        errors.append("Source guide, metadata, and collection citation coverage differ")
    if metadata["source_count"] != len(records):
        errors.append("Declared source count differs from unique metadata records")
    if len(records) != len(metadata["sources"]):
        errors.append("Duplicate source metadata IDs")
    for sid, record in sorted(records.items()):
        evidence_path = ROOT / record["evidence_path"]
        if not evidence_path.is_file():
            errors.append(f"[{sid}]: missing evidence")
            continue
        evidence = evidence_path.read_text()
        key = match_key(evidence)
        quotes = by_id[sid].get("quotes", [])
        if not quotes:
            errors.append(f"[{sid}]: no evidence excerpts")
        if record["url"] != by_id[sid]["url"] or record["quotes"] != quotes:
            errors.append(f"[{sid}]: metadata/ledger provenance mismatch")
        for quote in quotes:
            checked_quotes += 1
            if not match_key(quote["text"]) or match_key(quote["text"]) not in key:
                errors.append(f"[{sid}]: excerpt not found in saved body")
        if "──────── [TRUNCATED]" in evidence:
            errors.append(f"[{sid}]: evidence still contains truncation footer")

    expected_cases = {case["id"]: case["file"] for case in manifest["cases"]}
    if cases != expected_cases or len(expected_cases) != manifest["case_count"]:
        errors.append("Case headings/manifest/count disagree")
    for case in manifest["cases"]:
        body = (ROOT / case["file"]).read_text().split("\n## Sources\n", 1)[0]
        file_ids = {int(value) for value in CITE.findall(body)}
        if not set(case["source_ids"]).issubset(file_ids):
            errors.append(f"{case['id']}: manifest sources absent from case file")

    report = {"ok": not errors, "document_count": len(files),
              "case_count": len(cases), "cited_source_count": len(cited),
              "matched_evidence_quotes": checked_quotes,
              "checked_local_links": checked_links, "files": files, "errors": errors,
              "limits": "Structural and excerpt checks, not independent scientific replication or automated validation of every interpretation."}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
