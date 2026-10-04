"""Measure local evidence and verify the review artifacts without network access."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import re
import statistics
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
REVIEW = Path(__file__).resolve().parent.parent
SUPPORT = REVIEW / "_support"
SOURCES = ROOT / "colette-research/sources"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(name, value):
    path = SUPPORT / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def csv_rows(archive, member):
    with archive.open(member) as stream:
        yield from csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8"))


def measure():
    """Stream archives. Retain metadata only; MUST NOT emit credential values."""
    uq = SOURCES / "urlquery-net-data/urlquery-agent-activity-2026-09-23.zip"
    uscan = SOURCES / "us-can-data/us-canada-government-evidence-2026-09-30.zip"
    wiki = SOURCES / "rubygems-wiki-collusion/full-wiki-logs.zip"
    measured = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "sources": {}}
    for p in (uq, uscan, wiki):
        measured["sources"][str(p.relative_to(ROOT))] = {"sha256": sha(p), "bytes": p.stat().st_size}
    assigned = []
    with zipfile.ZipFile(uq) as archive:
        member = next(n for n in archive.namelist() if n.endswith("/report-sources.csv"))
        for r in csv_rows(archive, member):
            if r["data_source"] in ("US Census API", "AIHW", "SEC county data"):
                assigned.append({k: r[k] for k in ("report_id", "report_date_utc", "data_source", "source_basis")})
    measured["catalog_assignments"] = {}
    for source in ("US Census API", "AIHW", "SEC county data"):
        selected = sorted((r for r in assigned if r["data_source"] == source), key=lambda r: r["report_date_utc"])
        measured["catalog_assignments"][source] = {
            "report_count": len(selected), "first": selected[0], "last": selected[-1],
            "june17_18_reports": sum(r["report_date_utc"][:10] in ("2026-06-17", "2026-06-18") for r in selected),
        }
    sec_requests = []
    late = []
    capture_counts = Counter()
    capture_folders = {}
    with zipfile.ZipFile(uscan) as archive:
        for member in archive.namelist():
            if member.endswith("arquivo-captures.csv"):
                for r in csv_rows(archive, member):
                    capture_counts["all_capture_rows"] += 1
                    for term in ("zz=oai", "zzbulk", "prepnonce", "wbdisable"):
                        if term in r["target_url"]:
                            capture_counts[term] += 1
                            capture_folders.setdefault(term, Counter())[member.split("/")[-2]] += 1
            if member.endswith("14-sec/urlquery-reports.csv"):
                for rowno, r in enumerate(csv_rows(archive, member), 2):
                    if "2026-06-18T22:34:00Z" <= r["report_at_utc"] < "2026-06-18T23:28:00Z":
                        late.append({"report_id": r["report_id"], "report_time": r["report_at_utc"],
                                     "submitted_url_sha256": hashlib.sha256(r["submitted_url"].encode()).hexdigest(),
                                     "http_entries": int(r["http_entries"]), "raw_ref": f"{member}:CSV-record-{rowno}"})
            elif member.endswith("14-sec/urlquery-http.csv"):
                for rowno, r in enumerate(csv_rows(archive, member), 2):
                    if "county.json" in r["url"]:
                        sec_requests.append({"report_id": r["report_id"], "http_entry_index": r["http_entry_index"],
                                             "time": r["request_at_utc"], "status": r["http_status"],
                                             "response_mime": r["response_mime"], "response_sha256": r["response_sha256"],
                                             "body_in_source_json": r["response_body_in_source_json"],
                                             "method": r["method"], "url_sha256": hashlib.sha256(r["url"].encode()).hexdigest(),
                                             "raw_ref": f"{member}:CSV-record-{rowno}"})
    sec_requests.sort(key=lambda r: (r["time"], r["report_id"], r["http_entry_index"]))
    save("matrix-local-counts.json", {
        "method": "Literal case-sensitive substring in target_url; CSV row unit. No URL decoding.",
        "counts": dict(capture_counts),
        "by_folder": {k: dict(v) for k, v in capture_folders.items()},
    })
    measured["sec_http"] = {"unit": "exported HTTP entries with literal county.json in URL",
        "rows": len(sec_requests), "distinct_reports": len({r["report_id"] for r in sec_requests}),
        "first": sec_requests[0], "last": sec_requests[-1],
        "status_counts": dict(Counter(r["status"] for r in sec_requests)),
        "hour_counts": dict(sorted(Counter(r["time"][:13] for r in sec_requests).items())),
        "late_reports": late, "late_count": len(late),
        "late_unique_submitted_urls": len({r["submitted_url_sha256"] for r in late}),
        "late_declared_http_entries": sum(r["http_entries"] for r in late)}
    # A narrow local control. Missing bodies MUST remain a visibility limit.
    with zipfile.ZipFile(uscan) as archive:
        inventory = [{"member": n, "bytes": archive.getinfo(n).file_size} for n in archive.namelist()
                     if "/responses/" in n or n.endswith("response-excerpts.json")]
    measured["included_response_members"] = inventory
    measured["included_response_member_count"] = len(inventory)
    # Reconcile child CSVs independently; no source URLs are reconstituted.
    with (SUPPORT / "sec/cdx-events-redacted.csv").open() as stream:
        cdx = list(csv.DictReader(stream))
    times = sorted(datetime.fromisoformat(r["timestamp_utc"].replace("Z", "+00:00")) for r in cdx)
    peak = [t for t in times if t.hour == 20]
    measured["sec_cdx_recheck"] = {
        "rows": len(cdx), "urlkeys": len({r["urlkey_sha256"] for r in cdx}),
        "digests": dict(Counter(r["cdx_digest"] for r in cdx)),
        "first": times[0].isoformat(), "last": times[-1].isoformat(),
        "peak_rows": len(peak), "peak_span_seconds": (peak[-1] - peak[0]).total_seconds(),
        "peak_median_adjacent_gap_seconds": statistics.median((b-a).total_seconds() for a,b in zip(peak,peak[1:])),
    }
    save("parent-measurements.json", measured)
    print(json.dumps({"sec_http_rows": len(sec_requests), "late_reports": len(late),
                      "late_unique_urls": measured["sec_http"]["late_unique_submitted_urls"],
                      "included_response_members": len(inventory), "cdx_rows": len(cdx)}))


def verify():
    """Check parseability, links, citations, and report coverage."""
    errors = []
    expected = ["README.md", "SOURCE-GUIDE.md", "00-executive-result.md", "01-sec-wayback.md",
                "02-operation-linkage.md", "03-relay-layer.md", "04-census.md", "05-aihw.md",
                "06-dormancy-and-novelty.md", "07-chronology.md", "08-methods-and-reproducibility.md",
                "09-corrected-claims.md", "10-rejected-claims-and-open-questions.md",
                "11-stabilized-claim-state-2026-10-04.md"]
    for name in expected:
        if not (REVIEW / name).is_file(): errors.append(f"Missing {name}")
    readme = (REVIEW / "README.md").read_text() if (REVIEW / "README.md").exists() else ""
    for name in expected[1:]:
        if f"]({name})" not in readme: errors.append(f"README omits {name}")
    # Detect only the known exposed indicator, without logging or storing it.
    brief = (REVIEW.parent / "discord-brief-2026-10-03.md").read_text()
    secrets = set(re.findall(r"(?i)key=([0-9a-f]{30,64})", brief))
    ledger_paths = {
        'sec': SUPPORT / 'sec/citation-ledger.json',
        'relay': SUPPORT / 'relay/citation-ledger.json',
        'census-aihw': SUPPORT / 'census-aihw/citation-ledger.json',
        'novelty': SUPPORT / 'novelty/citations.json',
        'parent': SUPPORT / 'parent-citations.json',
    }
    ledgers = {
        name: {str(s['id']): s for s in json.loads(path.read_text())['sources']}
        for name, path in ledger_paths.items()
    }
    chapter_namespaces = {
        '01-sec-wayback.md': 'sec', '03-relay-layer.md': 'relay',
        '04-census.md': 'census-aihw', '05-aihw.md': 'census-aihw',
        '06-dormancy-and-novelty.md': 'novelty',
    }
    cited_keys = set()
    quote_gaps = {}
    inventory = []
    for p in sorted(REVIEW.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p == SUPPORT / 'verification.json': continue
        text = p.read_text(encoding='utf-8')
        if any(secret in text for secret in secrets): errors.append(f"Sensitive indicator present: {p.relative_to(REVIEW)}")
        try:
            if p.suffix == '.json': json.loads(text)
            elif p.suffix == '.jsonl':
                for line in text.splitlines():
                    if line.strip(): json.loads(line)
            elif p.suffix == '.py': ast.parse(text)
        except Exception as exc:
            errors.append(f"Parse failure: {p.relative_to(REVIEW)} ({type(exc).__name__})")
        if p.suffix == '.md':
            for dest in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in dest or dest.startswith('#') or dest.startswith('mailto:'): continue
                target = p.parent / dest.split('#')[0]
                if target.resolve() == SUPPORT / 'verification.json': continue
                if not target.exists(): errors.append(f"Broken link: {p.name} -> {dest}")
            # Evidence excerpts contain literal source syntax, not authored citations.
            if p.parent == REVIEW:
                body = text.split('\n## Sources')[0]
                used = set(re.findall(r'(?<!\!)\[(\d+)\](?!\()', body))
                definitions = dict(re.findall(r'^\[(\d+)\] (https?://\S+)', text, re.M))
                ns = chapter_namespaces.get(p.name, 'parent')
                if used != set(definitions): errors.append(f"Source-list mismatch: {p.name}")
                for sid in used:
                    cited_keys.add(f'{ns}:{sid}')
                    source = ledgers[ns].get(sid)
                    if not source or definitions.get(sid) != source['url']:
                        errors.append(f"Citation identity mismatch: {p.name}:{sid}")
                    elif not source.get('quotes'):
                        quote_gaps.setdefault(p.name, []).append(sid)
        inventory.append({'path':str(p.relative_to(REVIEW)), 'sha256':sha(p), 'bytes':p.stat().st_size})
    claims = []
    if not (SUPPORT / 'corrected-claims.json').is_file():
        errors.append('Missing corrected claim ledger')
    if (SUPPORT/'corrected-claims.json').exists():
        claims=json.loads((SUPPORT/'corrected-claims.json').read_text())
        if {r['original_item'] for r in claims} != {1,2,3,4,5,6}: errors.append('Six-item coverage failed')
        required={'claim_id','original_item','original_claim','surviving_claim','disposition','level',
                  'confidence','evidence','rejected_wording','alternative','missing_evidence','novelty','changes'}
        for r in claims:
            if not required <= r.keys(): errors.append(f"Incomplete claim: {r.get('claim_id')}")
    manifest = json.loads((SUPPORT / 'source-manifest.json').read_text())
    manifest_keys = {key for row in manifest['sources'] for key in row['namespace_keys']}
    if cited_keys != manifest_keys: errors.append('Source-guide citation coverage mismatch')
    for row in manifest['sources']:
        for path in row['retained_evidence']:
            if not (REVIEW / path).is_file(): errors.append(f'Missing evidence receipt: {path}')
    with (SUPPORT / 'strict-chronology.csv').open() as stream:
        chronology = list(csv.DictReader(stream))
    if len(chronology) != 74: errors.append('Strict chronology count differs from report')
    graph = json.loads((SUPPORT / 'operation-graph.json').read_text())
    nodes = {node['id'] for node in graph['nodes']}
    for edge in graph['edges']:
        if edge['from'] not in nodes or edge['to'] not in nodes: errors.append('Missing graph endpoint')
        if edge['operation_identity'] != 'unestablished': errors.append('Unreviewed identity upgrade')
        for ref in edge['source']:
            if ref == 'M1': continue
            ns, sid = ref.split(':', 1)
            if sid not in ledgers.get(ns, {}): errors.append(f'Invalid graph source: {ref}')
    replay = json.loads((SUPPORT / 'parent-replay-verification.json').read_text())
    if len(replay) != 4 or not all(r.get('matches_child') for r in replay):
        errors.append('Parent replay comparison failed')
    relay = json.loads((SUPPORT / 'relay/counts.json').read_text())['counts']
    if relay['raw_url_occurrences'] != 46278 or relay['hunk_insert_or_replace_county_urls'] != 32310:
        errors.append('Relay recount differs from report')
    executive = (REVIEW / '00-executive-result.md').read_text().split('\n## Sources')[0]
    if len(executive.split()) > 500: errors.append('Executive summary exceeds word limit')
    report={'verified_utc':datetime.now(timezone.utc).isoformat(),'errors':errors,'files':inventory,
            'root_documents': len(expected), 'source_records': len(manifest['sources']),
            'chronology_rows': len(chronology), 'claim_rows': len(claims),
            'citation_quote_attachment_gaps': quote_gaps,
            'scope':'Artifact checks only. Structured evidence receipts are separate from ledger quotes. '
                    'Missing quote attachments are disclosed, not treated as a passed evidence-quote gate. '
                    'These checks do not establish scientific entailment.'}
    save('verification.json',report)
    print(json.dumps({'errors':errors,'files_checked':len(inventory),
                      'documents': len(expected), 'source_records': len(manifest['sources']),
                      'quote_gate_passed': not quote_gaps}))
    return bool(errors)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('measure','verify'))
    args=parser.parse_args()
    if args.mode == 'measure': measure()
    else: raise SystemExit(verify())
