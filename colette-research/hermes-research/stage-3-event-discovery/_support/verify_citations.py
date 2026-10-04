#!/usr/bin/env python3
"""Strict chapter checks against cited subsets of the stable Stage 3 ledger.

The full-inventory, evidence-body and manifest checks live in verify_stage3.py.
Requires the installed grounded-citations skill; no third-party Python packages.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
ENGINE = HERMES_HOME / "skills/research/grounded-citations/scripts/sources.py"


def audit() -> dict:
    if not ENGINE.is_file():
        return {"status": "failed", "errors": [f"Citation engine unavailable: {ENGINE}"]}
    spec = importlib.util.spec_from_file_location("stage3_citation_engine", ENGINE)
    assert spec and spec.loader
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    sources = engine.load_ledger(ROOT / "_support/citation-ledger.json")["sources"]
    reports = []
    for path in sorted(ROOT.glob("*.md")):
        prose = path.read_text().split("## Sources", 1)[0]
        used = set(map(int, re.findall(r"(?<!\\)\[(\d+)\]", prose)))
        chapter_sources = [source for source in sources if source["id"] in used]
        code, errors, warnings = engine.verify_draft(
            path, chapter_sources, strict=True, require_evidence=True,
        )
        reports.append({
            "file": path.name, "exit_code": code,
            "errors": errors, "messages": warnings,
        })
    return {
        "status": "failed" if any(report["exit_code"] for report in reports) else "passed",
        "mode": "Strict per-chapter cited subsets; collection-wide source coverage checked separately.",
        "chapters": reports,
    }


def main() -> int:
    result = audit()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
