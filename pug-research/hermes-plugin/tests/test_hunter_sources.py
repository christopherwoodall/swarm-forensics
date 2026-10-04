"""Unit tests for hunter OSINT sources and dataset queries."""

import unittest

import support
from swarm_forensics_plugin import prompts, sources
from swarm_forensics_plugin.registry import DEFAULT_SOURCES
from swarm_forensics_plugin.research import Engine


class TestHunterSources(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()

    def tearDown(self):
        self.env.hunts.stop()
        self.env.close()

    def test_hunter_queries_defined(self):
        self.assertTrue(len(prompts.HUNTER_QUERIES) >= 4)
        for q in prompts.HUNTER_QUERIES:
            self.assertTrue("swarm" in q.lower() or "agent" in q.lower())

    def test_allowlist_includes_hunter_endpoints(self):
        self.assertIn("crt.sh", sources.ALLOWLIST)
        self.assertIn("export.arxiv.org", sources.ALLOWLIST)

    def test_default_sources_include_intel(self):
        names = [s["name"] for s in DEFAULT_SOURCES]
        self.assertIn("crt.sh", names)
        self.assertIn("arXiv Intelligence", names)

    def test_plan_user_includes_hunter_section(self):
        rendered = prompts.plan_user("investigate agents", [], [], [], [], 5)
        self.assertIn("Hunter intelligence templates", rendered)

    def test_plan_incorporates_hunter_queries(self):
        class DummyCtl:
            def stopped(self):
                return False

            def wait(self, _s):
                return False

        engine = Engine(self.env.parts, DummyCtl())
        cfg = {"hunt.max_queries_per_cycle": 6, "hunt.use_model": False}
        queries, _ = engine._plan("h1", "goal", cfg)
        has_hunter_query = any(hq in queries for hq in prompts.HUNTER_QUERIES)
        self.assertTrue(has_hunter_query)


if __name__ == "__main__":
    unittest.main()
