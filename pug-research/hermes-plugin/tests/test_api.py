"""Backend route tests. The FastAPI app runs in-process on a temp database."""

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from support import PLUGIN_DIR, FakeHermes, wait_for
from swarm_forensics_plugin.db import Database  # noqa: E402
from swarm_forensics_plugin.legacy import import_state  # noqa: E402
from swarm_forensics_plugin.service import Service  # noqa: E402

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    FastAPI = None


def _load_api():
    spec = importlib.util.spec_from_file_location(
        "sf_plugin_api", PLUGIN_DIR / "dashboard" / "plugin_api.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipIf(FastAPI is None, "fastapi is not installed")
class ApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.service = Service(Path(self.tmp.name) / "api.db", hermes=FakeHermes())
        self.service.settings.update({
            "hunt.sources": ["web"], "hunt.cycle_pause_seconds": 5})
        self.api = _load_api()
        self.api.get_service = lambda ctx=None: self.service
        self.api._started = True  # Skip the scheduler thread.
        app = FastAPI()
        app.include_router(self.api.router, prefix="/api/plugins/swarm-forensics")
        self.client = TestClient(app)
        self.base = "/api/plugins/swarm-forensics"

    def tearDown(self):
        self.service.hunts.shutdown.set()
        worker = self.service.hunts._worker
        if worker is not None:
            worker.join(timeout=10)
        self.tmp.cleanup()

    def get(self, path, **kw):
        return self.client.get(self.base + path, **kw)

    def post(self, path, body=None):
        return self.client.post(self.base + path, json=body if body is not None else {})

    def test_overview_and_settings(self):
        out = self.get("/overview").json()
        self.assertIn("capabilities", out)
        self.assertFalse(out["settings"]["schedule.enabled"]
                         if "schedule.enabled" in out["settings"] else False)
        cfg = self.get("/settings").json()
        self.assertIn("schema", cfg)
        bad = self.client.put(self.base + "/settings",
                              json={"updates": {"hunt.max_cycles": "many"}})
        self.assertEqual(bad.status_code, 422)

    def test_hunt_lifecycle(self):
        started = self.post("/hunts/start", {"goal": "test goal"})
        self.assertEqual(started.status_code, 200)
        hunt_id = started.json()["id"]
        again = self.post("/hunts/start", {})
        self.assertEqual(again.status_code, 409)
        self.assertEqual(self.post("/hunts/stop", {"hunt_id": hunt_id}).status_code, 200)
        self.assertTrue(wait_for(
            lambda: self.get("/hunts/%s" % hunt_id).json()["state"] == "stopped"))
        self.assertEqual(self.get("/hunts/missing").status_code, 404)

    def test_ioc_flow(self):
        added = self.post("/iocs", {"term": "zz=oaiflowtest", "category": "nonce_grammar"})
        self.assertEqual(added.status_code, 200)
        ioc = added.json()
        self.assertEqual(ioc["status"], "proposed")
        done = self.post("/iocs/%d/decision" % ioc["id"],
                         {"decision": "accept", "reason": "manual"})
        self.assertEqual(done.status_code, 200)
        self.assertEqual(done.json()["status"], "active")
        bad = self.post("/iocs/%d/decision" % ioc["id"], {"decision": "explode"})
        self.assertEqual(bad.status_code, 400)
        self.assertEqual(self.post("/iocs", {"term": ""}).status_code, 400)

    def test_entity_graph(self):
        a = self.post("/entities", {"type": "agent", "name": "Alpha",
                                    "notes": "Works with [[Beta]]."}).json()
        b = self.post("/entities", {"type": "swarm", "name": "Beta"}).json()
        link = self.post("/links", {"src": a["id"], "dst": b["id"], "kind": "member_of"})
        self.assertEqual(link.status_code, 200)
        graph = self.get("/graph", params={"center": a["id"]}).json()
        self.assertGreaterEqual(len(graph["nodes"]), 2)
        view = self.get("/entities/%s" % b["id"]).json()
        self.assertTrue(view["backlinks"] or view["links"])
        self.assertEqual(self.post("/entities", {"type": "nope", "name": "x"}).status_code, 400)
        self.assertEqual(self.client.delete(
            self.base + "/entities/%s" % a["id"]).status_code, 200)

    def test_schedule_is_opt_in(self):
        made = self.post("/schedules", {"name": "daily", "kind": "interval",
                                        "spec": "6h", "goal": "g"})
        self.assertEqual(made.status_code, 200)
        listed = self.get("/schedules").json()["schedules"]
        self.assertFalse(listed[0]["enabled"])
        sid = made.json()["id"]
        armed = self.post("/schedules/%s/arm" % sid, {"armed": True}).json()
        self.assertTrue(armed["schedules"][0]["enabled"])
        self.assertEqual(self.post("/schedules", {"name": "x", "kind": "weird",
                                                  "spec": "1"}).status_code, 400)

    def test_extract_preview(self):
        out = self.post("/extract-preview",
                        {"text": "see https://jqp.vercel.app/x?zz=oai123"}).json()
        self.assertTrue(out["indicators"])


class LegacyImportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state = root / "old" / "state"
        (self.state / "hits").mkdir(parents=True)
        (self.state / "iocs.json").write_text(json.dumps([
            {"term": "zz=oailegacy", "category": "nonce_grammar",
             "status": "active", "provenance": "seed"},
            {"term": "legacy-q.example", "status": "quarantined"}]))
        (self.state / "hits" / "2026-01-01.jsonl").write_text(json.dumps({
            "source": "urlquery", "query_id": "UQ-1", "term": "zz=oailegacy",
            "url": "https://example.test/p?zz=oailegacy&token=SECRET1234567890",
            "observed_utc": "2026-01-01T00:00:00Z", "evidence": "hit"}) + "\n")
        old = sqlite3.connect(self.state / "swarm-forensics.db")
        old.executescript("""
            CREATE TABLE entities(id TEXT, type TEXT, label TEXT, data_json TEXT,
                                  created_utc TEXT);
            CREATE TABLE relationships(from_id TEXT, to_id TEXT, rel TEXT);
            CREATE TABLE indicators(trace_id TEXT, kind TEXT, value TEXT);
            INSERT INTO entities VALUES ('a','agent','Old agent','{}','2026-01-01');
            INSERT INTO entities VALUES ('b','swarm','Old swarm','{}','2026-01-01');
            INSERT INTO relationships VALUES ('a','b','member_of');
            INSERT INTO indicators VALUES ('a','url','https://example.test/x');""")
        old.commit()
        old.close()
        self.db = Database(root / "new.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_import_is_complete_and_idempotent(self):
        first = import_state(self.db, self.state)
        self.assertEqual(first["iocs"], 2)
        self.assertEqual(first["evidence"], 1)
        self.assertEqual((first["entities"], first["links"], first["indicators"]),
                         (2, 1, 1))
        with self.db.connect() as conn:
            self.assertEqual(conn.execute(
                "SELECT status FROM iocs WHERE term = 'legacy-q.example'"
            ).fetchone()[0], "proposed")
            url = conn.execute("SELECT url FROM evidence").fetchone()[0]
        self.assertNotIn("SECRET1234567890", url)
        second = import_state(self.db, self.state)
        self.assertTrue(second.get("skipped"))
        with self.db.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM iocs").fetchone()[0], 2)


if __name__ == "__main__":
    unittest.main()
