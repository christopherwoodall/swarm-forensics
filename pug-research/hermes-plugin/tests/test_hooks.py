import tempfile
import unittest
from pathlib import Path

from support import FakeHermes
from swarm_forensics_plugin.hooks import LifecycleHooks, register_hooks
from swarm_forensics_plugin.service import Service


class HooksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = Service(Path(self.tmp.name) / "test.db", hermes=FakeHermes())
        self.hooks = LifecycleHooks(self.svc)

    def tearDown(self):
        self.svc.hunts.stop()
        self.svc.hunts.shutdown.set()
        for worker in list(self.svc.hunts._workers.values()):
            if worker.is_alive():
                worker.join(timeout=5)
        self.tmp.cleanup()

    def test_on_session_start_binds_active_hunt(self):
        hunt = self.svc.hunts.start("command", "test goal")
        self.hooks.on_session_start("ses-abc-123")
        bound = self.svc.ledger.hunt_for_session("ses-abc-123")
        self.assertIsNotNone(bound)
        self.assertEqual(bound["id"], hunt["id"])

    def test_pre_llm_call_injects_context(self):
        hunt = self.svc.hunts.start("command", "investigate relays", session_id="ses-llm-1")
        self.svc.ledger.bind_session(hunt["id"], "ses-llm-1")
        res = self.hooks.pre_llm_call("ses-llm-1")
        self.assertIsNotNone(res)
        self.assertIn("inject_system", res)
        self.assertIn("investigate relays", res["inject_system"])

    def test_pre_tool_call_enforces_pause(self):
        hunt = self.svc.hunts.start("command", "test goal", session_id="ses-tool-1")
        self.svc.ledger.bind_session(hunt["id"], "ses-tool-1")

        # Running hunt: tool allowed
        res_ok = self.hooks.pre_tool_call("web_search", {"query": "x"}, "ses-tool-1")
        self.assertIsNone(res_ok)

        # Paused hunt: tool aborted
        self.svc.hunts.pause(hunt["id"])
        res_paused = self.hooks.pre_tool_call("web_search", {"query": "x"}, "ses-tool-1")
        self.assertIsNotNone(res_paused)
        self.assertTrue(res_paused.get("abort"))

    def test_post_tool_call_records_web_search_and_extract(self):
        hunt = self.svc.hunts.start("command", "test goal", session_id="ses-obs-1")
        self.svc.ledger.bind_session(hunt["id"], "ses-obs-1")

        # Observe web_search
        self.hooks.post_tool_call(
            "web_search",
            {"query": "beacon trace"},
            [{"url": "https://example.com/observed_page", "title": "Observed"}],
            session_id="ses-obs-1",
        )
        obs = self.svc.ledger.corpus_observations(session_id="ses-obs-1")
        self.assertTrue(any(o["query_or_url"] == "beacon trace" for o in obs))
        self.assertIsNotNone(self.svc.urls.get("https://example.com/observed_page"))

        # Observe web_extract with auto-mirror
        self.hooks.post_tool_call(
            "web_extract",
            {"url": "https://example.com/observed_page"},
            [{"url": "https://example.com/observed_page", "content": "Body text with zz=oai100"}],
            session_id="ses-obs-1",
        )
        mirrored = self.svc.mirror.get_mirror("https://example.com/observed_page")
        self.assertIsNotNone(mirrored)
        self.assertGreater(mirrored["byte_count"], 0)

    def test_register_hooks(self):
        registered = {}

        class MockCtx:
            def register_hook(self, name, handler):
                registered[name] = handler

        ctx = MockCtx()
        register_hooks(ctx, self.svc)
        self.assertEqual(len(registered), 4)
        self.assertIn("on_session_start", registered)
        self.assertIn("pre_llm_call", registered)
        self.assertIn("pre_tool_call", registered)
        self.assertIn("post_tool_call", registered)


if __name__ == "__main__":
    unittest.main()
