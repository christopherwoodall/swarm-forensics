"""Backend route tests. The FastAPI app runs in-process on a temp database."""

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

from support import PLUGIN_DIR, FakeHermes, wait_for
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
        os.environ["SWARM_FORENSICS_STATE_DIR"] = self.tmp.name
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
        self.service.hunts.stop()
        self.service.hunts.shutdown.set()
        for worker in list(self.service.hunts._workers.values()):
            if worker.is_alive():
                worker.join(timeout=10)
        os.environ.pop("SWARM_FORENSICS_STATE_DIR", None)
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
        second = self.post("/hunts/start", {"goal": "another"})
        self.assertEqual(second.status_code, 200)
        second_id = second.json()["id"]
        self.assertNotEqual(second_id, hunt_id)
        self.client.put(self.base + "/settings",
                        json={"updates": {"hunt.max_active_hunts": 2}})
        capped = self.post("/hunts/start", {})
        self.assertEqual(capped.status_code, 409)
        self.assertEqual(self.post("/hunts/stop", {"hunt_id": hunt_id}).status_code, 200)
        self.assertTrue(wait_for(
            lambda: self.get("/hunts/%s" % hunt_id).json()["state"] == "stopped"))
        self.assertEqual(self.get("/hunts/missing").status_code, 404)
        self.post("/hunts/stop", {"hunt_id": second_id})

    def test_subhunt_spawn_and_children(self):
        started = self.post("/hunts/start", {"goal": "root hunt"})
        self.assertEqual(started.status_code, 200)
        parent_id = started.json()["id"]

        spawned = self.post("/hunts/%s/spawn" % parent_id, {"goal": "child hunt", "max_cycles": 1})
        self.assertEqual(spawned.status_code, 200)
        child = spawned.json()
        self.assertEqual(child["parent_hunt_id"], parent_id)
        self.assertEqual(child["depth"], 1)

        kids = self.get("/hunts/%s/children" % parent_id).json()
        self.assertEqual(len(kids["children"]), 1)
        self.assertEqual(kids["children"][0]["id"], child["id"])

        self.post("/hunts/stop", {"hunt_id": parent_id})
        self.assertTrue(wait_for(
            lambda: self.get("/hunts/%s" % parent_id).json()["state"] == "stopped"))
        self.assertTrue(wait_for(
            lambda: self.get("/hunts/%s" % child["id"]).json()["state"] == "stopped"))

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

    def test_events_filters(self):
        self.service.ledger.event("h1", "search", "search msg", level="info")
        self.service.ledger.event("h1", "sweep", "sweep warn", level="warn")
        self.service.ledger.event("h1", "search", "search err", level="error")

        all_evs = self.get("/events").json()["events"]
        self.assertGreaterEqual(len(all_evs), 3)

        search_evs = self.get("/events", params={"kind": "search"}).json()["events"]
        self.assertTrue(all(e["kind"] == "search" for e in search_evs))
        self.assertGreaterEqual(len(search_evs), 2)

        warn_evs = self.get("/events", params={"level": "warn"}).json()["events"]
        self.assertTrue(all(e["level"] == "warn" for e in warn_evs))
        self.assertGreaterEqual(len(warn_evs), 1)

    def test_lead_lifecycle(self):
        added = self.post("/leads", {"kind": "query", "value": "test query"}).json()
        self.assertTrue(added["added"])
        leads = self.get("/leads").json()["leads"]
        lead = next((row for row in leads if row["value"] == "test query"), None)
        self.assertIsNotNone(lead)

        res = self.post("/leads/%d/close" % lead["id"], {"status": "dismissed"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["closed"])

        leads_after = self.get("/leads").json()["leads"]
        self.assertNotIn(lead["id"], [row["id"] for row in leads_after])

        self.assertEqual(self.post("/leads/999999/close", {"status": "done"}).status_code, 404)
        err = self.post("/leads/%d/close" % lead["id"], {"status": "invalid"})
        self.assertEqual(err.status_code, 400)

    def test_sources_crud(self):
        sources = self.get("/sources").json()["sources"]
        self.assertGreaterEqual(len(sources), 4)

        created = self.post("/sources", {
            "name": "Custom CDX", "kind": "cdx",
            "endpoint": "https://custom.cdx.test/search",
            "note": "Custom index",
        })
        self.assertEqual(created.status_code, 200)
        sid = created.json()["id"]

        bad = self.post("/sources", {
            "name": "Bad", "kind": "cdx", "endpoint": "http://insecure.test"
        })
        self.assertEqual(bad.status_code, 400)

        put_res = self.client.put(
            self.base + "/sources/%d" % sid, json={"enabled": 1, "note": "Updated"}
        )
        updated = put_res.json()
        self.assertEqual(updated["enabled"], 1)
        self.assertEqual(updated["note"], "Updated")

        deleted = self.client.delete(self.base + "/sources/%d" % sid)
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(self.client.delete(self.base + "/sources/%d" % sid).status_code, 404)

    def test_grammar_and_wordlist(self):
        grammar = self.get("/grammar").json()["grammar"]
        self.assertGreater(len(grammar), 0)

        added = self.post("/grammar", {
            "kind": "pattern", "value": "https://api.test/{slot}",
        })
        self.assertEqual(added.status_code, 200)
        gid = added.json()["id"]

        toggled = self.client.put(self.base + "/grammar/%d" % gid, json={"enabled": False}).json()
        self.assertEqual(toggled["enabled"], 0)

        regen = self.post("/grammar/regenerate")
        self.assertEqual(regen.status_code, 200)
        self.assertIn("added", regen.json())

        imported = self.post("/iocs/import", {
            "text": "# SECTION Test\nterm-alpha.test\nterm-beta.test",
            "activate": True,
        })
        self.assertEqual(imported.status_code, 200)
        self.assertEqual(imported.json()["added"], 2)

    def test_export(self):
        a = self.post("/entities", {"type": "agent", "name": "Agent007",
                                    "notes": "Operates under [[SwarmSky]]."}).json()
        s = self.post("/entities", {"type": "swarm", "name": "SwarmSky"}).json()
        self.post("/links", {"src": a["id"], "dst": s["id"], "kind": "part_of"})
        self.post("/iocs", {"term": "sky-probe.test", "category": "domain", "activate": True})

        res = self.post("/export")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        export_path = Path(data["path"])
        self.assertTrue(export_path.exists())
        self.assertIn("counts", data)
        self.assertGreaterEqual(data["counts"]["entities"], 2)

        json_file = export_path / "swarm-forensics.json"
        self.assertTrue(json_file.exists())
        bundle = json.loads(json_file.read_text(encoding="utf-8"))
        self.assertEqual(bundle["schema"], 3)
        self.assertIn("exported_utc", bundle)
        self.assertIn("entities", bundle)
        self.assertIn("iocs", bundle)
        self.assertIn("urls", bundle)
        self.assertIn("prompts", bundle)

        vault = export_path / "vault"
        self.assertTrue(vault.exists())
        agent_note = vault / "Agents" / "Agent007.md"
        self.assertTrue(agent_note.exists())
        content = agent_note.read_text(encoding="utf-8")
        self.assertIn("[[SwarmSky]]", content)
        self.assertIn("type: agent", content)

        iocs_md = vault / "IOCs.md"
        self.assertTrue(iocs_md.exists())
        self.assertIn("sky-probe.test", iocs_md.read_text(encoding="utf-8"))

        prompts_dir = vault / "Prompts"
        self.assertTrue(prompts_dir.exists())

    def test_prompts_api(self):
        # List prompts
        res = self.client.get(self.base + "/prompts")
        self.assertEqual(res.status_code, 200)
        items = res.json()["prompts"]
        self.assertGreaterEqual(len(items), 5)

        # Get single prompt
        p = self.client.get(self.base + "/prompts/plan_system").json()
        self.assertEqual(p["id"], "plan_system")

        # Update prompt
        custom_txt = "Custom prompt text."
        put_res = self.client.put(
            self.base + "/prompts/plan_system", json={"template": custom_txt}
        )
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.json()["template"], custom_txt)

        # Reset prompt
        reset_res = self.post("/prompts/plan_system/reset")
        self.assertEqual(reset_res.status_code, 200)
        self.assertEqual(reset_res.json()["template"], p["default_template"])

        # Export and import prompts
        exp_res = self.client.get(self.base + "/prompts-export")
        self.assertEqual(exp_res.status_code, 200)
        self.assertIn("plan_system", exp_res.json()["prompts"])

        imp_res = self.post("/prompts-import", {
            "prompts": {"plan_system": {"template": "Imported prompt text."}}
        })
        self.assertEqual(imp_res.status_code, 200)
        self.assertEqual(imp_res.json()["imported"], 1)

    def test_urls_api(self):
        # Add URL via triage
        res = self.post("/urls/triage", {
            "url": "https://noisy.example/tracker.js",
            "status": "benign",
            "reason": "Known ad tracker",
        })
        self.assertEqual(res.status_code, 200)
        item = res.json()["item"]
        self.assertEqual(item["status"], "benign")

        # List URLs
        list_res = self.client.get(self.base + "/urls?status=benign")
        self.assertEqual(list_res.status_code, 200)
        data = list_res.json()
        self.assertGreaterEqual(len(data["urls"]), 1)
        self.assertIn("benign", data["counts"])
        self.assertGreaterEqual(data["counts"]["benign"], 1)

    def test_entity_groups_and_tags(self):
        # Create member agents
        a1 = self.post("/entities", {"type": "agent", "name": "Worker-A"}).json()
        self.post("/entities", {"type": "agent", "name": "Worker-B"}).json()

        # Create swarm group with members
        grp = self.post("/entities/group", {
            "type": "swarm",
            "name": "Phantom Swarm",
            "tags": ["recon", "stealth"],
            "members": ["Worker-A", "Worker-B"],
        })
        self.assertEqual(grp.status_code, 200)
        grp_data = grp.json()
        self.assertEqual(grp_data["members_linked"], 2)
        self.assertIn("stealth", grp_data["entity"]["tags"])

        # Tag entity endpoint
        tag_res = self.post(f"/entities/{a1['id']}/tag", {"tags": ["high-prio"]})
        self.assertEqual(tag_res.status_code, 200)
        self.assertIn("high-prio", tag_res.json()["tags"])

    def test_iocs_benign_decision(self):
        ioc = self.post("/iocs", {"term": "benign-relay.example/c2=1"}).json()
        dec_res = self.post(f"/iocs/{ioc['id']}/decision", {
            "decision": "benign",
            "reason": "Verified benign CDN",
        })
        self.assertEqual(dec_res.status_code, 200)
        self.assertEqual(dec_res.json()["status"], "benign")

    def test_reset_endpoint(self):
        self.post("/entities", {"type": "agent", "name": "EphemeralAgent"})
        self.post("/iocs", {"term": "ephemeral.example"})
        res = self.post("/reset", {})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["ok"])
        entities = self.get("/entities").json()["entities"]
        self.assertEqual(len(entities), 0)
        iocs = self.get("/iocs").json()["iocs"]
        ioc_terms = [i["term"] for i in iocs]
        self.assertNotIn("ephemeral.example", ioc_terms)
        self.assertGreaterEqual(len(iocs), 1)
        urls = self.get("/urls").json()["urls"]
        self.assertEqual(len(urls), 0)

    def test_session_and_mirror_endpoints(self):
        hunt = self.service.hunts.start("command", "session api test", session_id="ses-api-1")
        bind_res = self.post("/sessions/ses-api-1/bind", {"hunt_id": hunt["id"]})
        self.assertEqual(bind_res.status_code, 200)

        overview = self.get("/sessions/ses-api-1/overview").json()
        self.assertEqual(overview["session_id"], "ses-api-1")
        self.assertEqual(overview["hunt"]["id"], hunt["id"])

        m = self.service.mirror.save_extract(
            "https://example.com/api_mirror", "Mirrored text sample"
        )
        self.assertIsNotNone(m)

        mirrors_res = self.get("/mirrors").json()
        self.assertGreaterEqual(mirrors_res["total"], 1)

        detail_res = self.get(f"/mirrors/{m['sha256']}?include_text=true").json()
        self.assertEqual(detail_res["url"], "https://example.com/api_mirror")
        self.assertEqual(detail_res["content"], "Mirrored text sample")

        self.service.ledger.record_corpus_observation(
            hunt_id=hunt["id"], session_id="ses-api-1", tool_name="web_search",
            query_or_url="query text", status="observed",
        )
        corpus_res = self.get("/corpus?session_id=ses-api-1").json()
        self.assertEqual(len(corpus_res["observations"]), 1)



if __name__ == "__main__":
    unittest.main()
