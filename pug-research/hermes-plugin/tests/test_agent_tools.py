import json
import tempfile
import unittest
from pathlib import Path

from support import FakeHermes, fake_index_getter
from swarm_forensics_plugin.agent_tools import (
    register_tools,
    sf_analyze_corpus,
    sf_attach_hunt,
    sf_get_context,
    sf_link_entities,
    sf_manage_entity,
    sf_mirror_url,
    sf_propose_ioc,
    sf_query_knowledge,
    sf_record_evidence,
    sf_search_index,
    sf_spawn_subhunt,
    sf_triage_item,
)
from swarm_forensics_plugin.service import Service


class AgentToolsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = Service(Path(self.tmp.name) / "test.db", hermes=FakeHermes())
        self.svc.parts.getter = fake_index_getter({
            "default": [
                ["original", "timestamp", "statuscode", "digest"],
                ["https://example.com/sub", "20240101", "200", "DIGEST1"],
            ]
        })

    def tearDown(self):
        self.svc.hunts.stop()
        self.svc.hunts.shutdown.set()
        for worker in list(self.svc.hunts._workers.values()):
            if worker.is_alive():
                worker.join(timeout=10)
        self.tmp.cleanup()

    def test_sf_get_context(self):
        res = json.loads(sf_get_context({}, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertIn("status", res)
        self.assertIn("entity_counts", res)
        self.assertIn("active_iocs", res)

    def test_sf_search_index(self):
        # Empty query error
        err = json.loads(sf_search_index({"query": ""}, service=self.svc))
        self.assertFalse(err["ok"])
        self.assertIn("query must not be empty", err["error"])

        # Valid mock search
        res = json.loads(sf_search_index({"source": "cdx", "query": "example.com"},
                                          service=self.svc))
        self.assertTrue(res["ok"])
        self.assertEqual(res["source"], "cdx")

    def test_sf_record_evidence(self):
        res = json.loads(sf_record_evidence({
            "url": "https://example.com/bot_net",
            "query": "bot_net",
            "source": "web",
            "excerpt": "active beacon found in user agent header",
            "claim_level": "L3",
        }, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertGreater(res["evidence_id"], 0)
        self.assertEqual(res["url"], "https://example.com/bot_net")

        # Verify recorded into url store
        self.assertIsNotNone(self.svc.urls.get("https://example.com/bot_net"))

    def test_sf_propose_ioc(self):
        res = json.loads(sf_propose_ioc({
            "term": "relay.botnet.example/c2=1",
            "category": "relay",
            "reason": "Relay node observed in telemetry",
        }, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertEqual(res["ioc"]["term"], "relay.botnet.example/c2=1")
        self.assertEqual(res["ioc"]["status"], "proposed")

    def test_sf_manage_entity(self):
        # Upsert swarm group
        res = json.loads(sf_manage_entity({
            "action": "upsert",
            "type": "swarm",
            "name": "Cobalt Swarm Alpha",
            "summary": "Coordinated crawler swarm",
            "tags": ["recon", "stealth"],
            "notes": "Observed targeting payment gateways.",
        }, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertEqual(res["entity"]["name"], "Cobalt Swarm Alpha")
        self.assertIn("recon", res["entity"]["tags"])

        # Tag entity action
        tag_res = json.loads(sf_manage_entity({
            "action": "tag",
            "name": "Cobalt Swarm Alpha",
            "tags": ["high-priority"],
        }, service=self.svc))
        self.assertTrue(tag_res["ok"])
        self.assertIn("high-priority", tag_res["entity"]["tags"])
        self.assertIn("recon", tag_res["entity"]["tags"])

        # Get entity action
        get_res = json.loads(sf_manage_entity({
            "action": "get",
            "name": "Cobalt Swarm Alpha",
        }, service=self.svc))
        self.assertTrue(get_res["ok"])
        self.assertEqual(get_res["entity"]["name"], "Cobalt Swarm Alpha")

    def test_sf_link_entities(self):
        # Create parent swarm and child agent
        sf_manage_entity({
            "action": "upsert",
            "type": "swarm",
            "name": "Delta Swarm",
        }, service=self.svc)
        sf_manage_entity({
            "action": "upsert",
            "type": "agent",
            "name": "Crawler-42",
        }, service=self.svc)

        # Hierarchical link (agent -> part_of -> swarm)
        hier_res = json.loads(sf_link_entities({
            "src_name": "Crawler-42",
            "dst_name": "Delta Swarm",
            "kind": "part_of",
        }, service=self.svc))
        self.assertTrue(hier_res["ok"])

        # Loose connection (associated_with)
        loose_res = json.loads(sf_link_entities({
            "src_name": "Crawler-42",
            "dst_name": "Delta Swarm",
            "kind": "associated_with",
        }, service=self.svc))
        self.assertTrue(loose_res["ok"])

    def test_sf_triage_item(self):
        # Triage URL as benign
        self.svc.urls.add("https://safe-cdn.example/static.js", "safe-cdn.example", "web")
        url_res = json.loads(sf_triage_item({
            "item_type": "url",
            "target": "https://safe-cdn.example/static.js",
            "verdict": "benign",
            "reason": "Legitimate CDN script",
        }, service=self.svc))
        self.assertTrue(url_res["ok"])
        self.assertEqual(url_res["item"]["status"], "benign")
        self.assertTrue(self.svc.urls.is_benign("https://safe-cdn.example/static.js"))

        # Triage IOC as benign
        ioc, _ = self.svc.iocs.propose("harmless.example/test=1")
        ioc_res = json.loads(sf_triage_item({
            "item_type": "ioc",
            "target": "harmless.example/test=1",
            "verdict": "benign",
            "reason": "Confirmed researcher infrastructure",
        }, service=self.svc))
        self.assertTrue(ioc_res["ok"])
        self.assertEqual(ioc_res["item"]["status"], "benign")

        # Triage lead
        self.svc.ledger.add_lead("query", "search_term", priority=1.0)
        leads = self.svc.ledger.open_leads("query", limit=1)
        lid = leads[0]["id"]
        lead_res = json.loads(sf_triage_item({
            "item_type": "lead",
            "target": str(lid),
            "verdict": "dismissed",
            "reason": "Not fruitful",
        }, service=self.svc))
        self.assertTrue(lead_res["ok"])
        self.assertTrue(lead_res["closed"])

    def test_sf_query_knowledge(self):
        sf_manage_entity({
            "action": "upsert",
            "type": "agent",
            "name": "ReconBot-9000",
            "summary": "Autonomous scanner agent",
            "tags": ["scanner"],
        }, service=self.svc)

        res = json.loads(sf_query_knowledge({
            "query": "ReconBot",
            "kind": "all",
        }, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertGreaterEqual(len(res["entities"]), 1)
        self.assertEqual(res["entities"][0]["name"], "ReconBot-9000")

    def test_sf_spawn_subhunt(self):
        parent = self.svc.hunts.start("test", "root investigation")
        res = json.loads(sf_spawn_subhunt({
            "parent_hunt_id": parent["id"],
            "goal": "investigate child swarm",
            "max_cycles": 2,
        }, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertEqual(res["parent_hunt_id"], parent["id"])
        self.assertEqual(res["depth"], 1)
        self.svc.hunts.stop()

    def test_sf_attach_hunt(self):
        hunt = self.svc.hunts.start("test", "root investigation", session_id="ses-12345")
        res = json.loads(sf_attach_hunt({
            "target": hunt["id"],
        }, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertEqual(res["hunt"]["id"], hunt["id"])
        self.assertEqual(res["hunt"]["session_id"], "ses-12345")

        # By session ID
        res_by_ses = json.loads(sf_attach_hunt({
            "target": "ses-12345",
        }, service=self.svc))
        self.assertTrue(res_by_ses["ok"])
        self.assertEqual(res_by_ses["hunt"]["id"], hunt["id"])
        self.svc.hunts.stop()

    def test_sf_mirror_url(self):
        res = json.loads(sf_mirror_url({
            "url": "https://example.com/mirrored_report",
            "content": "Observed relay token zz=oai12345 in header",
        }, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertEqual(res["mirror"]["url"], "https://example.com/mirrored_report")
        self.assertTrue(self.svc.mirror.get_mirror("https://example.com/mirrored_report"))

    def test_sf_analyze_corpus(self):
        # Seed an observation and evidence
        sf_record_evidence({
            "url": "https://jqp.vercel.app/api/v0?jq=.data&url=https%3A%2F%2Ftarget.example%2Fapi%3Fzz%3Doai999",
            "query": "target.example",
            "source": "web",
            "excerpt": "Relay trace zz=oai999",
        }, service=self.svc)

        res = json.loads(sf_analyze_corpus({}, service=self.svc))
        self.assertTrue(res["ok"])
        self.assertGreaterEqual(res["total_corpus_urls"], 1)
        self.assertTrue(any(r["relay_host"] == "jqp.vercel.app" for r in res["observed_relays"]))

    def test_register_tools_context(self):
        registered = []

        class MockCtx:
            def register_tool(self, **kwargs):
                registered.append(kwargs)

        ctx = MockCtx()
        register_tools(ctx)
        self.assertEqual(len(registered), 12)
        names = {r["name"] for r in registered}
        self.assertIn("sf_get_context", names)
        self.assertIn("sf_search_index", names)
        self.assertIn("sf_record_evidence", names)
        self.assertIn("sf_mirror_url", names)
        self.assertIn("sf_analyze_corpus", names)
        self.assertIn("sf_propose_ioc", names)
        self.assertIn("sf_manage_entity", names)
        self.assertIn("sf_link_entities", names)
        self.assertIn("sf_triage_item", names)
        self.assertIn("sf_query_knowledge", names)
        self.assertIn("sf_spawn_subhunt", names)
        self.assertIn("sf_attach_hunt", names)


if __name__ == "__main__":
    unittest.main()
