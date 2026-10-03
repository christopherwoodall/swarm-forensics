#!/usr/bin/env python3
"""Static server for the stage-4 trace viewer. Binds to loopback only.

Serves the viewer directory plus one JSON API endpoint that streams bounded
queries against data/raw/traces/events.jsonl without loading it into memory.

Usage:
    python3 serve.py [--port 8002]
"""

from __future__ import annotations

import argparse
import http.server
import json
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EVENTS = REPO / "data" / "raw" / "traces" / "events.jsonl"
HOST = "127.0.0.1"
PUBLIC_SUFFIXES = {".html", ".js", ".json", ".css"}
MAX_ROWS = 200
# The query endpoint streams the complete events file. Substring prefilters
# keep it fast; matches are capped at MAX_ROWS. A bounded prefix scan would
# silently miss datasets stored later in the file, so correctness requires
# the full pass.
DATASET_NEEDLE = '"dataset": "'


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serve public files and one bounded query endpoint."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    # -- static files ------------------------------------------------------

    def _allowed(self) -> bool:
        route = self.path.split("?", 1)[0].split("#", 1)[0]
        if route == "/":
            self.path = "/index.html"
            route = self.path
        try:
            target = (HERE / urllib.parse.unquote(route).lstrip("/")).resolve()
        except (OSError, ValueError):
            return False
        if HERE not in target.parents:
            return False
        return target.suffix in PUBLIC_SUFFIXES and not any(
            part.startswith(".") for part in target.relative_to(HERE).parts
        )

    # -- query endpoint ----------------------------------------------------

    def _query(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        dataset = (params.get("dataset", [""])[0] or "").strip()
        needle = (params.get("q", [""])[0] or "").strip().lower()
        limit = min(int(params.get("limit", ["50"])[0]) or 50, MAX_ROWS)
        matches: list[dict] = []
        scanned = 0
        ds_needle = f"{DATASET_NEEDLE}{dataset}\"" if dataset else ""
        if EVENTS.exists():
            with open(EVENTS, encoding="utf-8") as handle:
                for line in handle:
                    scanned += 1
                    line = line.strip()
                    if not line:
                        continue
                    # Cheap substring prefilters before JSON parsing.
                    if ds_needle and ds_needle not in line:
                        continue
                    if needle and needle not in line.lower():
                        continue
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    matches.append(row)
                    if len(matches) >= limit:
                        break
        body = json.dumps({"scanned": scanned, "rows": matches}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/events"):
            self._query()
        elif self._allowed():
            super().do_GET()
        else:
            self.send_error(404, "Not found")

    def do_HEAD(self):
        if self._allowed():
            super().do_HEAD()
        else:
            self.send_error(404, "Not found")

    def list_directory(self, path):
        self.send_error(404, "Not found")


def make_server(port: int) -> http.server.ThreadingHTTPServer:
    return http.server.ThreadingHTTPServer((HOST, port), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8002)
    args = parser.parse_args(argv)
    server = make_server(args.port)
    print(f"Serving on http://{HOST}:{args.port}/index.html (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
