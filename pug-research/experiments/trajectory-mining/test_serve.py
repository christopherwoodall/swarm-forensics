"""Offline tests: the loopback server and its read-only JSON API."""

from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import serve
from importer import TrajectoryImporter
from test_fixtures import generate_synthetic_dataset


class ServeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls._tmp.name)
        generate_synthetic_dataset(tmp / "raw", big_turns=100)
        imp = TrajectoryImporter(tmp / "raw", tmp / "i.db", progress=None)
        imp.run_all()
        imp.conn.close()
        cls.server = serve.make_server(0, tmp / "i.db", quiet=True)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.missing = serve.make_server(0, tmp / "none.db", quiet=True)
        threading.Thread(target=cls.missing.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        for s in (cls.server, cls.missing):
            s.shutdown()
            s.server_close()
        cls._tmp.cleanup()

    def get(self, path, port=None, headers=None):
        req = urllib.request.Request(f"http://127.0.0.1:{port or self.port}{path}", headers=headers or {})
        try:
            with urllib.request.urlopen(req) as res:
                return res.status, res.read(), dict(res.headers)
        except urllib.error.HTTPError as err:
            try:
                return err.code, err.read(), dict(err.headers)
            finally:
                err.close()

    def test_binds_loopback_only(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_serves_only_the_fixed_file_list(self):
        status, body, headers = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"<html", body.lower())
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual(self.get("/vendor/three.module.js")[0], 200)
        for path in ("/serve.py", "/../pyproject.toml", "/vendor/../db.py", "/%2e%2e/db.py",
                     "/test_fixtures.py", "/vendor/", "/PROMPT.md"):  # fmt: skip
            self.assertEqual(self.get(path)[0], 404, path)

    def test_rejects_foreign_host_header(self):
        status, _body, _h = self.get("/api/overview", headers={"Host": "evil.example.com"})
        self.assertEqual(status, 403)

    def test_api_overview_traces_graph_steps(self):
        status, body, _ = self.get("/api/overview")
        self.assertEqual(status, 200)
        overview = json.loads(body)
        self.assertEqual(overview["trace_types"]["computer_use"], 7)
        status, body, _ = self.get("/api/traces?type=computer_use&agent=agent-1")
        self.assertEqual({t["trace_id"] for t in json.loads(body)["traces"]}, {"session:s1", "session:s3"})
        status, body, _ = self.get("/api/graph?trace=session:s1&trace=session:s3&max_nodes=60")
        graph = json.loads(body)
        self.assertEqual(status, 200)
        self.assertLessEqual(len(graph["nodes"]), 60)
        status, body, _ = self.get("/api/steps?trace=session:s-big&limit=5&per_trace=40")
        self.assertEqual(len(json.loads(body)["steps"]), 5)

    def test_bad_requests_return_400_without_values(self):
        status, body, _ = self.get("/api/traces?from=SECRET-not-a-date")
        self.assertEqual(status, 400)
        self.assertNotIn(b"SECRET", body)
        status, body, _ = self.get("/api/graph?trace=session:SECRET-missing")
        self.assertEqual(status, 400)
        self.assertNotIn(b"SECRET", body)
        self.assertEqual(self.get("/api/graph?max_nodes=abc&trace=session:s1")[0], 400)
        self.assertEqual(self.get("/api/nope")[0], 404)
        many = "&".join("trace=session:s1" for _ in range(30))
        self.assertEqual(self.get(f"/api/graph?{many}")[0], 200)  # capped to 20, deduplicated

    def test_missing_index_gives_503_hint(self):
        status, body, _ = self.get("/api/overview", port=self.missing.server_address[1])
        self.assertEqual(status, 503)
        self.assertEqual(json.loads(body)["error"], "index_missing")


if __name__ == "__main__":
    unittest.main()
