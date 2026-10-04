import unittest

import support
from swarm_forensics_plugin import predict
from swarm_forensics_plugin.registry import Registry, RegistryError
from swarm_forensics_plugin.sources import host_allowed


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.reg = self.env.registry

    def tearDown(self):
        self.env.close()

    def test_seeded_sources_and_grammar(self):
        sources = self.reg.sources()
        self.assertGreaterEqual(len(sources), 4)
        enabled_sources = self.reg.sources(enabled_only=True)
        # Default seeds: Wayback CDX (on), arquivo.pt (on), urlquery (off), Common Crawl (off)
        enabled_names = {s["name"] for s in enabled_sources}
        self.assertIn("Wayback CDX", enabled_names)
        self.assertIn("Arquivo.pt", enabled_names)
        self.assertNotIn("urlquery.net", enabled_names)
        self.assertNotIn("Common Crawl", enabled_names)

        # Prober is set
        prober = self.reg.candidate_prober()
        self.assertIsNotNone(prober)
        self.assertEqual(prober["name"], "Wayback CDX")

        # Grammar bundle
        bundle = self.reg.grammar_bundle()
        self.assertGreater(len(bundle["patterns"]), 0)
        self.assertIn("jqp.vercel.app", bundle["relays"])
        self.assertIn("zz", bundle["nonce_probes"])

    def test_source_validation(self):
        with self.assertRaises(RegistryError):
            self.reg.add_source("", "cdx", "https://example.com/cdx")
        with self.assertRaises(RegistryError):
            self.reg.add_source("Custom", "invalid_kind", "https://example.com/cdx")
        # Insecure scheme (http)
        with self.assertRaises(RegistryError):
            self.reg.add_source("Insecure", "cdx", "http://example.com/cdx")
        # Localhost / private IP
        with self.assertRaises(RegistryError):
            self.reg.add_source("Local", "cdx", "https://localhost/cdx")
        with self.assertRaises(RegistryError):
            self.reg.add_source("Private", "cdx", "https://127.0.0.1/cdx")
        # Bad config key
        with self.assertRaises(RegistryError):
            self.reg.add_source("BadCfg", "cdx", "https://example.com/cdx", config={"bad_key": 1})

    def test_source_crud_and_allowed_hosts(self):
        initial_hosts = self.reg.allowed_hosts()
        self.assertIn("web.archive.org", initial_hosts)
        self.assertIn("arquivo.pt", initial_hosts)
        self.assertNotIn("urlquery.net", initial_hosts)

        # Add new source
        src = self.reg.add_source("Test Archive", "cdx", "https://archive.example.org/cdx",
                                  config={"filter_field": "urlkey"}, note="Test source")
        self.assertTrue(src["enabled"])
        self.assertIn("archive.example.org", self.reg.allowed_hosts())
        self.assertTrue(host_allowed("https://archive.example.org/cdx?q=test", self.reg.allowed_hosts()))

        # Disable source
        self.reg.update_source(src["id"], enabled=False)
        self.assertNotIn("archive.example.org", self.reg.allowed_hosts())
        self.assertFalse(host_allowed("https://archive.example.org/cdx?q=test", self.reg.allowed_hosts()))

        # Delete source
        deleted = self.reg.delete_source(src["id"])
        self.assertTrue(deleted)
        self.assertIsNone(self.reg.get_source(src["id"]))

    def test_grammar_matches_old_candidates(self):
        default_candidates = predict.generate_candidates()
        bundle = self.reg.grammar_bundle()
        bundle_candidates = predict.generate_candidates(bundle)
        self.assertEqual(set(default_candidates), set(bundle_candidates))

    def test_grammar_crud(self):
        initial_count = len(self.reg.grammar())
        item = self.reg.add_grammar("pattern", "https://api.example.com/v1/{int}")
        self.assertEqual(item["kind"], "pattern")
        self.assertTrue(item["enabled"])

        # Disable grammar
        self.reg.set_grammar_enabled(item["id"], False)
        bundle = self.reg.grammar_bundle()
        self.assertNotIn("https://api.example.com/v1/{int}", bundle["patterns"])

        # Delete grammar
        self.assertTrue(self.reg.delete_grammar(item["id"]))
        self.assertEqual(len(self.reg.grammar()), initial_count)

    def test_wordlist_import(self):
        text = """# TOOLKIT
tool_pattern_alpha
tool_pattern_beta

# RELAY
new.relay.example.com
"""
        result = self.reg.import_wordlist(text, self.env.iocs, activate=True)
        self.assertEqual(result["added"], 3)
        self.assertEqual(result["refused"], 0)

        # Verify imported terms are active
        active = self.env.iocs.active_terms()
        self.assertIn("tool_pattern_alpha", active)
        self.assertIn("new.relay.example.com", active)

        # Import again: duplicate terms should be skipped
        result2 = self.reg.import_wordlist(text, self.env.iocs)
        self.assertEqual(result2["added"], 0)
        self.assertEqual(result2["skipped"], 3)

    def test_registry_writes_audit_events(self):
        before_events = self.env.ledger.events()
        self.reg.add_grammar("jq_probe", ".custom_probe")
        after_events = self.env.ledger.events()
        registry_events = [e for e in after_events["events"] if e["kind"] == "registry"]
        self.assertGreater(len(registry_events), 0)
        self.assertIn(".custom_probe", registry_events[-1]["message"])


if __name__ == "__main__":
    unittest.main()
