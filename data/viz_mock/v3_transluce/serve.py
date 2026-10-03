#!/usr/bin/env python3
"""Static server for the pivot graph viewer. Binds to loopback only.

Usage:
    python3 serve.py [--port 8001]

The server exposes only `.html`, `.js`, and `.json` files inside this directory.
It refuses every other path, hidden files, and any path that leaves this directory.
"""

from __future__ import annotations

import argparse
import http.server
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PUBLIC_SUFFIXES = {".html", ".js", ".json"}


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serve public files only."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def _allowed(self) -> bool:
        route = self.path.split("?", 1)[0].split("#", 1)[0]
        if route == "/":
            self.path = "/index.html"
            route = self.path
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
        if self._allowed():
            super().do_GET()
        else:
            self.send_error(404, "Not found")

    def do_HEAD(self) -> None:
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
    parser.add_argument("--port", type=int, default=8001)
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
