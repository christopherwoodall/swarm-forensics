"""Loopback server for the trajectory 3D viewer.

Binds to 127.0.0.1 only. Serves a fixed list of public files and a small read-only JSON API.
Each request opens the index read-only and returns a bounded slice.
Error bodies never include request values, record values, or stack traces.
"""

from __future__ import annotations

import argparse
import http.server
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import db  # noqa: E402
from catalog import MAX_STEPS_PAGE, CatalogError, TraceCatalog  # noqa: E402
from contract import ContractError  # noqa: E402

HOST = "127.0.0.1"
DEFAULT_PORT = 8002
PUBLIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/vendor/three.module.js": ("vendor/three.module.js", "text/javascript"),
    "/vendor/OrbitControls.js": ("vendor/OrbitControls.js", "text/javascript"),
}
MAX_PARAM_CHARS = 200
CSP = (
    "default-src 'self'; style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline'; img-src 'self' data:"
)


def _int(query: dict[str, list[str]], key: str, default: int) -> int:
    raw = query.get(key, [str(default)])[0]
    if not raw.lstrip("-").isdigit():
        raise CatalogError("numeric parameter expected")
    return int(raw)


def _one(query: dict[str, list[str]], key: str) -> str | None:
    value = query.get(key, [None])[0]
    if value is not None and len(value) > MAX_PARAM_CHARS:
        raise CatalogError("parameter too long")
    return value or None


def _many(query: dict[str, list[str]], key: str, limit: int = 40) -> list[str]:
    values = [v for v in query.get(key, []) if v][:limit]
    if any(len(v) > MAX_PARAM_CHARS for v in values):
        raise CatalogError("parameter too long")
    return values


class Handler(http.server.BaseHTTPRequestHandler):
    db_path: Path = db.DEFAULT_DB_PATH
    server_version = "TrajectoryViewer"
    quiet: bool = False

    def log_request(self, code: Any = "-", size: Any = "-") -> None:
        """Log method, path, and status. The query string stays out of the log."""
        if self.quiet:
            return
        path = urlparse(self.path).path
        sys.stderr.write(f"{self.address_string()} {self.command} {path} {code}\n")

    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: Any) -> None:
        self._send(status, json.dumps(data).encode("utf-8"), "application/json")

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return host in ("127.0.0.1", "localhost")

    def do_GET(self) -> None:
        if not self._host_ok():
            self._json(403, {"error": "forbidden_host"})
            return
        parsed = urlparse(self.path)
        route = parsed.path
        if route in PUBLIC_FILES:
            name, ctype = PUBLIC_FILES[route]
            try:
                self._send(200, (HERE / name).read_bytes(), ctype)
            except OSError:
                self._json(404, {"error": "not_found"})
            return
        if route.startswith("/api/"):
            self._api(route, parse_qs(parsed.query))
            return
        self._json(404, {"error": "not_found"})

    def _api(self, route: str, query: dict[str, list[str]]) -> None:
        try:
            conn = db.connect(self.db_path, readonly=True)
        except FileNotFoundError:
            self._json(503, {"error": "index_missing", "hint": "run make index"})
            return
        except (db.IndexVersionError, sqlite3.Error):
            self._json(503, {"error": "index_unreadable", "hint": "rebuild the index"})
            return
        try:
            catalog = TraceCatalog(conn)
            if route == "/api/overview":
                data: Any = catalog.overview()
            elif route == "/api/traces":
                data = catalog.search_traces(
                    agent_ids=_many(query, "agent") or None,
                    goal_id=_one(query, "goal"),
                    types=_many(query, "type") or None,
                    date_from=_one(query, "from"),
                    date_to=_one(query, "to"),
                    q=_one(query, "q"),
                    limit=_int(query, "limit", 50),
                    offset=_int(query, "offset", 0),
                )
            elif route == "/api/graph":
                data = catalog.graph(
                    _many(query, "trace", 20),
                    max_nodes=_int(query, "max_nodes", 400),
                    include_inferred=_one(query, "inferred") != "0",
                )
            elif route == "/api/steps":
                data = catalog.steps(
                    _one(query, "trace") or "",
                    offset=_int(query, "offset", 0),
                    limit=_int(query, "limit", min(100, MAX_STEPS_PAGE)),
                    per_trace=_int(query, "per_trace", 40),
                )
            else:
                self._json(404, {"error": "not_found"})
                return
            self._json(200, data)
        except CatalogError as err:
            self._json(400, {"error": "bad_request", "reason": str(err)})
        except (sqlite3.Error, ContractError, OSError) as err:
            self._json(500, {"error": "server_error", "type": type(err).__name__})
        finally:
            conn.close()


def make_server(port: int, db_path: Path, quiet: bool = False) -> http.server.ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {"db_path": Path(db_path), "quiet": quiet})
    return http.server.ThreadingHTTPServer((HOST, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the trajectory 3D viewer (loopback only).")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--db", type=Path, default=db.DEFAULT_DB_PATH)
    args = parser.parse_args()
    server = make_server(args.port, args.db)
    print(f"Trajectory viewer at http://{HOST}:{server.server_address[1]}/ (index: {args.db})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
