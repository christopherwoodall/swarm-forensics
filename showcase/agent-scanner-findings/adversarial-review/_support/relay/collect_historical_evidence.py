#!/usr/bin/env python3
"""Preserve redacted metadata from public relay archives.

MUST NOT submit target URLs to a relay or save raw report bodies.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent / "historical-evidence.json"
CDX = "https://web.archive.org/cdx/search/cdx"
HOSTS = ["jqp.vercel.app/api/v0", "allorigins.hexlet.app", "api.cors.lol", "platform.lemino.ai"]
REPORT_IDS = [
    "830d0a0c-d9d4-483d-9149-c33c35bf2f84",
    "eb91d8ad-2f82-40df-803f-5474539757c1",
    "a9d4b7db-2921-40d9-aa1b-01d6927b9731",
]


def get_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=40) as response:
        return json.load(response)


def collect() -> None:
    evidence: dict = {"archive_index": {}, "urlquery_reports": {}}
    for host in HOSTS:
        query = urllib.parse.urlencode({
            "url": host, "matchType": "prefix", "from": "20260101", "to": "20260618",
            "fl": "timestamp,original,statuscode,mimetype,digest", "output": "json", "limit": "1000",
        })
        endpoint = CDX + "?" + query
        response = get_json(endpoint)
        rows = response[1:] if response else []
        evidence["archive_index"][host] = {
            "source_url": endpoint, "method": "public Wayback CDX GET, no collapse",
            "rows_returned_bounded": len(rows), "limit": 1000,
            "status_200_rows": sum(row[2] == "200" for row in rows),
            "earliest_rows": [
                {"capture_timestamp_utc": row[0],
                 "outer_host": urllib.parse.urlsplit(row[1]).hostname,
                 "path": urllib.parse.urlsplit(row[1]).path,
                 "statuscode": row[2], "mimetype": row[3], "digest": row[4]}
                for row in sorted(rows)[:3]
            ],
        }
    for report_id in REPORT_IDS:
        url = f"https://urlquery.net/report/{report_id}/json"
        doc = get_json(url)
        http_rows = []
        for record in doc.get("http", []):
            response = record.get("response") or {}
            body = response.get("data") or {}
            http_rows.append({
                "time_utc": record.get("date"),
                "host": (record.get("url") or {}).get("fqdn"),
                "method": (record.get("request") or {}).get("method"),
                "response_status": response.get("status_code"),
                "response_size_bytes": body.get("size"),
                "response_sha256": body.get("sha256"),
                "response_mime": body.get("mime_type"),
                "body_available_in_report": bool(body.get("data")),
            })
        evidence["urlquery_reports"][report_id] = {
            "source_url": url, "method": "public urlquery report JSON GET",
            "report_time_utc": doc.get("date"),
            "submitted_host": (doc.get("url") or {}).get("fqdn"),
            "final_host": (doc.get("final") or {}).get("url", {}).get("fqdn"),
            "http": http_rows,
        }
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    collect()
