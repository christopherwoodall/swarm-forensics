"""Offline tests for the pivot graph check, its viewer server, and the static page."""

import contextlib
import http.client
import importlib.util
import io
import json
import re
import tempfile
import threading
import unittest
from pathlib import Path

from swarm_forensics import pivot
from swarm_forensics.replay import ReplayError

ROOT = Path(__file__).resolve().parents[2]
VIZ = ROOT / "data" / "viz_mock" / "v3_transluce"


def small_graph() -> dict:
    node = {"note": "n", "badge": None, "dim": False, "size": 5}
    return {
        "meta": {"source": "s", "day0": "2026-01-01", "day1": "2026-01-03", "ndays": 3, "note": "n", "nodes": 4, "edges": 3},
        "nodes": [
            {"id": "L:a", "layer": "launcher", "label": "a", **node},
            {"id": "P:b", "layer": "pivot", "label": "b", **node},
            {"id": "T:c", "layer": "target", "label": "c", **node},
            {"id": "S:d", "layer": "source", "label": "d", **node, "badge": "CANDIDATE"},
        ],
        "edges": [
            {"a": "L:a", "b": "P:b", "w": 3, "label": "3 events"},
            {"a": "P:b", "b": "T:c", "w": 2, "label": "2 events"},
            {"a": "S:d", "b": "L:a", "w": 1, "conf": "candidate", "label": "1 event"},
        ],
        "days": [
            {"d": "2026-01-01", "n": {"L:a": 1}, "digest": []},
            {"d": "2026-01-02", "n": {"P:b": 2}, "digest": ["line"]},
            {"d": "2026-01-03", "n": {}, "digest": []},
        ],
    }


class GraphTests(unittest.TestCase):
    def test_small_graph_is_valid(self):
        pivot.validate_graph(small_graph())

    def test_shipped_graph_is_valid(self):
        graph = pivot.load_graph(VIZ / "data" / "graph.json")
        self.assertEqual(len(graph["days"]), graph["meta"]["ndays"])

    def test_rejects_broken_graphs(self):
        def mutate(change):
            graph = small_graph()
            change(graph)
            return graph

        broken = {
            "missing section": lambda g: g.pop("edges"),
            "meta key": lambda g: g["meta"].pop("source"),
            "bad date": lambda g: g["meta"].update(day0="soon"),
            "ndays": lambda g: g["meta"].update(ndays=9),
            "layer": lambda g: g["nodes"][0].update(layer="other"),
            "prefix": lambda g: g["nodes"][0].update(id="X:a"),
            "duplicate id": lambda g: g["nodes"][1].update(id="L:a", layer="launcher"),
            "size": lambda g: g["nodes"][0].update(size=-1),
            "bool size": lambda g: g["nodes"][0].update(size=True),
            "badge": lambda g: g["nodes"][0].update(badge="hot"),
            "badge on launcher": lambda g: g["nodes"][0].update(badge="CONFIRMED"),
            "source without badge": lambda g: g["nodes"][3].update(badge=None),
            "edge confidence": lambda g: g["edges"][2].update(conf="sure"),
            "missing confidence": lambda g: g["edges"][2].pop("conf"),
            "confidence off source": lambda g: g["edges"][0].update(conf="confirmed"),
            "meta node count": lambda g: g["meta"].update(nodes=9),
            "meta edge count": lambda g: g["meta"].update(edges=9),
            "dim": lambda g: g["nodes"][0].update(dim="no"),
            "edge ref": lambda g: g["edges"][0].update(b="P:zzz"),
            "edge direction": lambda g: g["edges"][0].update(a="T:c", b="L:a"),
            "edge weight": lambda g: g["edges"][0].update(w=0),
            "day count": lambda g: g["days"].pop(),
            "day order": lambda g: g["days"][1].update(d="2026-02-02"),
            "day node": lambda g: g["days"][0]["n"].update({"P:nope": 1}),
            "day count value": lambda g: g["days"][0]["n"].update({"L:a": -3}),
            "digest": lambda g: g["days"][0].update(digest="text"),
            "missing layer": lambda g: g.update(nodes=g["nodes"][:3], edges=g["edges"][:2]),
        }
        for name, change in broken.items():
            with self.subTest(name), self.assertRaises(ReplayError):
                pivot.validate_graph(mutate(change))
        with self.assertRaises(ReplayError):
            pivot.validate_graph([])

    def test_error_messages_hide_values(self):
        graph = small_graph()
        graph["nodes"][0]["size"] = "topsecret"
        with self.assertRaises(ReplayError) as caught:
            pivot.validate_graph(graph)
        self.assertNotIn("topsecret", str(caught.exception))

    def test_load_errors_and_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ReplayError):
                pivot.load_graph(root / "absent.json")
            bad = root / "bad.json"
            bad.write_text('{"secret": "topsecret" BROKEN', encoding="utf-8")
            with self.assertRaises(ReplayError) as caught:
                pivot.load_graph(bad)
            self.assertNotIn("topsecret", str(caught.exception))
            good = root / "good.json"
            good.write_text(json.dumps(small_graph()), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(pivot.main(["--file", str(good)]), 0)
            self.assertIn("4 nodes, 3 edges, 3 days", out.getvalue())
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(pivot.main(["--file", str(bad)]), 1)
            self.assertIn("Error:", errors.getvalue())


class ServeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("pivot_serve", VIZ / "serve.py")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.module.Handler.log_message = lambda *args: None
        cls.server = cls.module.make_server(0)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def fetch(self, path: str, method: str = "GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request(method, path)
            response = conn.getresponse()
            return response.status, response.getheader("Content-Type", ""), response.read()
        finally:
            conn.close()

    def test_binds_to_loopback(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_public_files_are_served(self):
        for path in ("/", "/index.html", "/data/graph.json", "/vendor/OrbitControls.js", "/vendor/three.module.js"):
            self.assertEqual(self.fetch(path)[0], 200, path)
        self.assertEqual(self.fetch("/data/graph.json", "HEAD")[0], 200)
        self.assertIn("javascript", self.fetch("/vendor/OrbitControls.js")[1])

    def test_everything_else_is_refused(self):
        for path in (
            "/serve.py", "/README.md", "/vendor/", "/data/", "/../README.md", "/%2e%2e/%2e%2e/README.md",
            "/..%2f..%2fdata/raw/events.jsonl.gz", "/vendor/../serve.py", "/.hidden.json", "/missing.html",
        ):
            with self.subTest(path):
                self.assertEqual(self.fetch(path)[0], 404)


class FrontendTests(unittest.TestCase):
    """Static checks on the browser file. No browser runs here."""

    @classmethod
    def setUpClass(cls):
        cls.page = (VIZ / "index.html").read_text(encoding="utf-8")

    def test_loads_only_local_resources(self):
        self.assertNotIn("http://", self.page)
        self.assertNotIn("https://", self.page)
        self.assertNotIn("data:", self.page)
        self.assertIn("./vendor/three.module.js", self.page)

    def test_reads_one_data_route(self):
        self.assertEqual(re.findall(r"fetch\(([^)]*)\)", self.page), ["'./data/graph.json'"])

    def test_renders_data_text_safely(self):
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
            self.assertNotIn(banned, self.page)

    def test_has_v2_playback_controls(self):
        for control in ("btn-play", "btn-prev", "btn-next", "btn-reset", "btn-view", "speed", "scrub"):
            self.assertIn(f'id="{control}"', self.page)

    def test_playback_does_not_move_the_camera(self):
        for banned in ("autoFocus", "camera.position.lerp", "flyTo", "enableZoom = false", "enablePan = false"):
            self.assertNotIn(banned, self.page)

    def test_page_knows_all_tiers_and_confidences(self):
        for name in ("source", "launcher", "pivot", "target"):
            self.assertRegex(self.page, rf"\n  {name}:\s+{{ y:")
        for badge in ("CONFIRMED", "CANDIDATE", "HYPOTHESIS", "HONEST GAP"):
            self.assertIn(f"'{badge}':", self.page)
        for conf in ("confirmed", "candidate", "hypothesized"):
            self.assertRegex(self.page, rf"\n  {conf}:\s+{{ lit:")

    def test_quiet_nodes_stay_visible(self):
        match = re.search(r"const QUIET_OPACITY = ([0-9.]+);", self.page)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(float(match.group(1)), 0.4)
        self.assertIn("? 1 : QUIET_OPACITY", self.page)
        self.assertIn("opacity: QUIET_OPACITY", self.page)

    def test_data_holds_markup_like_text(self):
        graph = json.loads((VIZ / "data" / "graph.json").read_text(encoding="utf-8"))
        tagged = [n["id"] for n in graph["nodes"] if "<" in n["note"] or "<" in n["label"]]
        self.assertTrue(tagged, "the data holds markup-like text, so textContent is required")


if __name__ == "__main__":
    unittest.main()
