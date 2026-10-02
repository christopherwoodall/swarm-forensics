#!/usr/bin/env python3
"""Audit the Stage 3 dossier; this is not a scientific replication."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
CITE = re.compile(r"(?<!\\)\[(\d+)\]")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MD_LINK = re.compile(r"\[([^\]]*)\]\((?:[^()\s]|\([^()]*\))*\)")
PARTS = [
    "What happened", "Why it is relevant", "What evidence exists",
    "Autonomy and control topology", "Coordination substrate",
    "Strong claims versus speculative claims", "Distinctness",
]


def key(text: str) -> str:
    text = MD_LINK.sub(r"\1", text)
    text = re.sub(r"[*_`~]|\\(?=[^\w\s])", "", text)
    return " ".join(text.split()).casefold()


def audit(draft: bool = False) -> dict:
    ledger = json.loads((ROOT / "_support/citation-ledger.json").read_text())
    records = json.loads((ROOT / "_support/source-records.json").read_text())
    sources = {s["id"]: s for s in ledger["sources"]}
    metadata = {s["id"]: s for s in records}
    errors: list[str] = []
    manifest_path = ROOT / "_support/case-manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    if not draft and manifest is None:
        errors.append("Final case manifest missing")
    files = sorted(ROOT.glob("*.md"))
    if manifest and set(manifest["documents"]) != {f.name for f in files}:
        errors.append("Document inventory disagrees with manifest")
    if len(metadata) != len(records):
        errors.append("Duplicate source-record IDs")
    if len({s["url"] for s in sources.values()}) != len(sources):
        errors.append("Duplicate normalized source URLs")

    cited: set[int] = set()
    hashes: dict[str, str] = {}
    quote_count = 0
    card_locations: dict[str, tuple[str, str]] = {}
    card_cited: set[int] = set()
    sizes: list[dict] = []
    for path in files:
        text = path.read_text()
        parts = re.split(r"(?m)^## Sources\s*$", text)
        body = parts[0]
        used = set(map(int, CITE.findall(body)))
        cited |= used
        if used and len(parts) != 2:
            errors.append(f"{path.name}: missing/duplicate Sources block")
        if used and len(parts) == 2:
            listed = {}
            for line in parts[1].splitlines():
                match = re.match(r"\[(\d+)\]\s+(https?://\S+)", line)
                if match:
                    listed[int(match[1])] = match[2]
            if set(listed) != used:
                errors.append(f"{path.name}: source list differs from inline citations")
            for sid, url in listed.items():
                if sid not in sources or url != sources[sid]["url"]:
                    errors.append(f"{path.name}: source [{sid}] URL disagrees with ledger")
        for target in LINK.findall(body):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            local = unquote(target.split("#", 1)[0])
            if local and not (path.parent / local).exists():
                errors.append(f"{path.name}: broken link {target}")
        if re.search(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", body):
            errors.append(f"{path.name}: unresolved placeholder")
        sections = re.split(r"(?m)^## (S3-[A-Z0-9-]+) — ", body)
        for i in range(1, len(sections), 2):
            cid, content = sections[i:i + 2]
            if cid in card_locations:
                errors.append(f"Duplicate case heading {cid}")
            card_locations[cid] = (path.name, content)
            card_cited.update(map(int, CITE.findall(content)))
            headings = re.findall(r"(?m)^### ([1-7])\. (.+)$", content)
            if headings != [(str(i + 1), part) for i, part in enumerate(PARTS)]:
                errors.append(f"{cid}: seven required dimensions missing or reordered")
            if not CITE.search(content):
                errors.append(f"{cid}: no supporting citation")
        sizes.append({"file": path.name, "words": len(text.split()), "bytes": path.stat().st_size})

    for sid in sorted(cited):
        if sid not in sources or sid not in metadata:
            errors.append(f"Missing ledger/metadata for source [{sid}]")
            continue
        record = metadata[sid]
        if record["url"] != sources[sid]["url"]:
            errors.append(f"Source [{sid}]: metadata URL mismatch")
        ep = ROOT / record["evidence_path"]
        if not ep.is_file():
            errors.append(f"Source [{sid}]: durable evidence missing")
            continue
        evidence = ep.read_text()
        hashes[record["evidence_path"]] = hashlib.sha256(ep.read_bytes()).hexdigest()
        quotes = [q["text"] for q in sources[sid].get("quotes", [])]
        if not quotes:
            errors.append(f"Source [{sid}]: no evidence quote")
        for quote in quotes:
            quote_count += 1
            if key(quote) not in key(evidence):
                errors.append(f"Source [{sid}]: quote not found in saved evidence")
        for field in ("date", "type", "limits"):
            if not record.get(field):
                errors.append(f"Source [{sid}]: no {field}")
        # A publication after the explicit research cutoff cannot support this pass.
        dates = re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", record["date"])
        if manifest and any(d > manifest["research_cutoff"] for d in dates):
            errors.append(f"Source [{sid}]: date after research cutoff")

    category_counts: dict[str, int] = {}
    if manifest:
        cases = manifest["candidates"]
        ids = [c["id"] for c in cases]
        if len(ids) != len(set(ids)) or set(ids) != set(card_locations):
            errors.append("Case manifest does not match distinct candidate headings")
        if manifest["candidate_count"] != len(cases):
            errors.append("Declared candidate count does not match manifest")
        for case in cases:
            cid = case["id"]
            if case["document"] != card_locations.get(cid, (None,))[0]:
                errors.append(f"{cid}: wrong document in manifest")
            if not case.get("distinctness") or not case.get("evidence_class"):
                errors.append(f"{cid}: missing evidence/distinctness classification")
            category = case["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        if category_counts != manifest["category_counts"]:
            errors.append("Declared category counts do not match cases")
        count_groups = {
            "primary_event_match_count": {"field_campaign", "engineering_run", "field_experiment"},
            "boundary_comparator_count": {"boundary_case"},
            "mechanism_exception_count": {"controlled_propagation", "simulation_exception"},
        }
        for field, categories in count_groups.items():
            actual = sum(category_counts.get(category, 0) for category in categories)
            if manifest.get(field) != actual:
                errors.append(f"Declared {field} disagrees with case categories")
        if manifest.get("card_source_count") != len(card_cited):
            errors.append("Declared card-source count disagrees with card citations")
        if manifest.get("source_record_count") != len(records):
            errors.append("Declared source-record count disagrees with metadata")
        guide = ROOT / "08-annotated-source-guide.md"
        guide_body = guide.read_text().split("## Sources", 1)[0] if guide.exists() else ""
        guide_cited = set(map(int, CITE.findall(guide_body)))
        if guide_cited != set(manifest["guide_source_ids"]):
            errors.append("Source-guide citations disagree with declared guide coverage")
        if not set(manifest["guide_source_ids"]) >= cited:
            errors.append("Source guide does not cover cited-source union")
        if set(sources) != cited or set(metadata) != cited:
            errors.append("Final source inventory contains uncited or unregistered records")
    return {
        "status": "failed" if errors else ("draft_checks_passed" if draft else "passed"),
        "errors": errors,
        "documents": sizes,
        "candidate_count": len(card_locations),
        "category_counts": category_counts,
        "cited_source_count": len(cited),
        "card_source_count": len(card_cited),
        "checked_quote_count": quote_count,
        "evidence_hashes": hashes,
        "limitations": "Checks structure and preserved evidence, not causal inference, authorship, experimental replication or every sentence's entailment.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()
    result = audit(args.draft)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
