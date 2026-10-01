#!/usr/bin/env python3
"""Static server for the AI Village viz mocks. Binds to loopback only.

Usage:
    python3 serve.py [--case PATH] [--port 8000]

The server exposes a fixed set of public files from this directory. It maps `/case.json`
to the file given by `--case`. The case file lives under the ignored `data/raw/` tree.
The server never serves `data/raw/` itself, and it refuses any other path.
"""

from __future__ import annotations

import argparse
import http.server
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
DEFAULT_CASE = HERE.parents[2] / "data" / "raw" / "replay" / "sample-case.json"
PUBLIC_SUFFIXES = {".html", ".js", ".json"}
CASE_ROUTE = "/case.json"
MAX_CASE_BYTES = 20 * 1024 * 1024


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serve public files and one explicit case route."""

    case_path: Path = DEFAULT_CASE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def _route(self) -> str:
        return self.path.split("?", 1)[0].split("#", 1)[0]

    def _send_case(self, head_only: bool) -> None:
        path = self.case_path
        try:
            size = path.stat().st_size
            if not path.is_file() or size > MAX_CASE_BYTES:
                raise OSError
            body = b"" if head_only else path.read_bytes()
        except OSError:
            self.send_error(404, "Case file not found. Run the replay export first.")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(size))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _allowed(self, route: str) -> bool:
        try:
            target = (HERE / unquote(route).lstrip("/")).resolve()
        except (OSError, ValueError):
            return False
        if HERE not in target.parents:
            return False
        return target.suffix in PUBLIC_SUFFIXES and not any(
            part.startswith(".") for part in target.relative_to(HERE).parts
        )

    def do_GET(self) -> None:
        route = self._route()
        if route == CASE_ROUTE:
            self._send_case(head_only=False)
        elif self._allowed(route):
            super().do_GET()
        else:
            self.send_error(404, "Not found")

    def do_HEAD(self) -> None:
        route = self._route()
        if route == CASE_ROUTE:
            self._send_case(head_only=True)
        elif self._allowed(route):
            super().do_HEAD()
        else:
            self.send_error(404, "Not found")

    def list_directory(self, path):
        self.send_error(404, "Not found")


def make_server(port: int, case_path: Path) -> http.server.ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {"case_path": Path(case_path)})
    return http.server.ThreadingHTTPServer((HOST, port), handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE, help="case JSON to serve")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    server = make_server(args.port, args.case)
    print(f"Serving on http://{HOST}:{args.port}/workflow-player.html (Ctrl+C to stop)")
    print(f"Case file: {args.case}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
