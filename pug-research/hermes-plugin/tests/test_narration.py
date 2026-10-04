import time
import unittest

import support
from swarm_forensics_plugin import session_env
from swarm_forensics_plugin.narration import Narrator


class FakeCtx:
    """Stand-in for the plugin context with an inject_message bridge."""

    def __init__(self, allow=True):
        self.posts = []  # (session_key, content)
        self.allow = allow

    def inject_message(self, content, session_key=None):
        if not self.allow:
            return False
        self.posts.append((session_key, content))
        return True


class SvcStub:
    """Narrator-facing view over the shared test environment."""

    def __init__(self, env):
        self.settings = env.settings
        self.ledger = env.ledger


class NarrationTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.env.settings.update({
            "narrate.min_interval_seconds": 60,
            "narrate.drive_idle_seconds": 120,
        })
        self.svc = SvcStub(self.env)
        self.ctx = FakeCtx()
        self.narrator = Narrator(self.svc)
        self.narrator.attach(self.ctx)

    def tearDown(self):
        self.narrator.stop()
        self.env.close()

    def _bound_hunt(self, origin="desktop"):
        hunt = self.env.ledger.create_hunt(origin, "goal")
        self.env.ledger.bind_session(hunt["id"], "sess1", "durable1")
        return hunt

    def _expire_throttle(self, hunt_id):
        for key in list(self.narrator._last_post):
            if key[0] == hunt_id:
                self.narrator._last_post[key] = time.monotonic() - 7200

    def test_first_tick_skips_backlog_then_posts_digest(self):
        hunt = self._bound_hunt()
        self.env.ledger.event(hunt["id"], "search", "old: backlog item")
        self.narrator.tick()  # cursor init; the backlog is not reposted
        self.assertEqual(self.ctx.posts, [])

        self.env.ledger.event(hunt["id"], "search", "web: zz=oai -> 3 results")
        self.env.ledger.event(hunt["id"], "plan", "sweep the nonce grammar next")
        self.narrator.tick()
        self.assertEqual(len(self.ctx.posts), 1)
        target, text = self.ctx.posts[0]
        self.assertEqual(target, "durable1")
        self.assertIn("[swarm-forensics] hunt %s" % hunt["id"][:8], text)
        self.assertIn("[search] web: zz=oai -> 3 results", text)
        self.assertIn("thinking: sweep the nonce grammar next", text)
        self.assertNotIn("backlog item", text)

        self.narrator.tick()  # nothing new: no repeat
        self.assertEqual(len(self.ctx.posts), 1)

    def test_digest_is_throttled_and_cursor_waits(self):
        hunt = self._bound_hunt()
        self.narrator.tick()
        self.env.ledger.event(hunt["id"], "search", "first batch")
        self.narrator.tick()
        self.assertEqual(len(self.ctx.posts), 1)

        self.env.ledger.event(hunt["id"], "finding", "second batch")
        self.narrator.tick()  # inside min_interval: held back
        self.assertEqual(len(self.ctx.posts), 1)

        self._expire_throttle(hunt["id"])
        self.narrator.tick()
        self.assertEqual(len(self.ctx.posts), 2)
        self.assertIn("second batch", self.ctx.posts[1][1])

    def test_denial_sets_blocked_flag_and_success_clears_it(self):
        hunt = self._bound_hunt()
        self.narrator.tick()  # cursor init
        self.ctx.allow = False
        self.env.ledger.event(hunt["id"], "search", "denied post")
        self.narrator.tick()
        self.assertEqual(self.ctx.posts, [])
        self.assertEqual(self.env.ledger.cursor("narrate", "blocked"), "1")
        self.assertTrue(self.env.hunts.status()["narration_blocked"])

        self.ctx.allow = True
        self._expire_throttle(hunt["id"])
        self.narrator.tick()
        self.assertTrue(self.ctx.posts)
        self.assertIn("denied post", self.ctx.posts[-1][1])
        self.assertEqual(self.env.ledger.cursor("narrate", "blocked"), "0")
        self.assertFalse(self.env.hunts.status()["narration_blocked"])

    def test_dead_target_is_muted_and_does_not_hold_the_flag(self):
        hunt = self._bound_hunt()
        self.narrator.tick()  # cursor init
        self.ctx.allow = False
        for i in range(3):
            self.env.ledger.event(hunt["id"], "search", "batch %d" % i)
            self.narrator._last_post.clear()
            self.narrator.tick()
        self.assertIn("durable1", self.narrator._target_muted)
        self.assertEqual(self.env.ledger.cursor("narrate", "blocked"), "1")

        # A live session on another hunt succeeds and clears the flag.
        other = self.env.ledger.create_hunt("session", "other")
        self.env.ledger.bind_session(other["id"], "sess2", "live2")
        self.ctx.allow = True
        self.narrator.tick()  # cursor init for the new pair
        self.env.ledger.event(other["id"], "search", "live post")
        self.narrator.tick()
        self.assertIn("live2", [t for t, _ in self.ctx.posts])
        self.assertEqual(self.env.ledger.cursor("narrate", "blocked"), "0")

        # The dead target stays quiet inside the mute window.
        self.env.ledger.event(hunt["id"], "search", "batch 3")
        self.narrator._last_post.clear()
        self.narrator.tick()
        self.assertNotIn("durable1", [t for t, _ in self.ctx.posts])

        # After the window it retries once and recovers when allowed.
        self.narrator._target_muted["durable1"] = time.monotonic() - 1
        self.narrator._last_post.clear()
        self.narrator.tick()
        self.assertIn("durable1", [t for t, _ in self.ctx.posts])
        self.assertNotIn("durable1", self.narrator._target_failures)

    def test_fresh_session_hunt_gets_an_immediate_kickoff(self):
        hunt = self._bound_hunt(origin="session")
        self.narrator.tick()  # no idle wait for a hunt that never started
        kicks = [p for p in self.ctx.posts if "is ready" in p[1]]
        self.assertEqual(len(kicks), 1)
        self.assertIn("sf_get_context", kicks[0][1])
        self.assertEqual(self.narrator._dry_drives[hunt["id"]], 1)
        self.narrator.tick()  # no repeat while the agent has not answered
        self.assertEqual(
            len([p for p in self.ctx.posts if "is ready" in p[1]]), 1)

    def test_idle_session_hunt_gets_a_drive_prompt(self):
        hunt = self._bound_hunt(origin="session")
        self.narrator.tick()  # kickoff
        self.assertIn("is ready", self.ctx.posts[0][1])
        self.env.ledger.event(hunt["id"], "search", "agent did work")
        self.narrator.tick()  # activity resets the clock
        self.narrator._last_activity[hunt["id"]] = time.monotonic() - 3600
        self.narrator.tick()
        drives = [p for p in self.ctx.posts if "is idle" in p[1]]
        self.assertEqual(len(drives), 1)
        self.assertIn("sf_get_context", drives[0][1])
        self.assertEqual(self.narrator._dry_drives[hunt["id"]], 1)

    def test_drive_stops_after_three_dry_prompts(self):
        hunt = self._bound_hunt(origin="session")
        self.narrator.tick()
        self.narrator._last_activity[hunt["id"]] = time.monotonic() - 3600
        self.narrator._dry_drives[hunt["id"]] = 3
        self.narrator.tick()
        self.assertEqual([p for p in self.ctx.posts if "is idle" in p[1]], [])

    def test_new_activity_resets_the_drive_clock(self):
        hunt = self._bound_hunt(origin="session")
        self.narrator.tick()
        self.narrator._last_activity[hunt["id"]] = time.monotonic() - 3600
        self.narrator._dry_drives[hunt["id"]] = 2
        self.env.ledger.event(hunt["id"], "search", "fresh work")
        self.narrator.tick()
        self.assertEqual(self.narrator._dry_drives[hunt["id"]], 0)
        self.assertEqual([p for p in self.ctx.posts if "is idle" in p[1]], [])

    def test_non_session_hunt_is_not_driven(self):
        hunt = self._bound_hunt(origin="desktop")
        self.narrator.tick()
        self.narrator._last_activity[hunt["id"]] = time.monotonic() - 3600
        self.narrator.tick()
        self.assertEqual([p for p in self.ctx.posts if "is idle" in p[1]], [])

    def test_disabled_narration_posts_nothing(self):
        hunt = self._bound_hunt()
        self.env.settings.update({"narrate.enabled": False})
        self.env.ledger.event(hunt["id"], "search", "quiet")
        self.narrator.tick()
        self.assertEqual(self.ctx.posts, [])

    def test_unbound_hunt_is_ignored(self):
        hunt = self.env.ledger.create_hunt("session", "goal")
        self.env.ledger.event(hunt["id"], "search", "nobody listening")
        self.narrator.tick()
        self.assertEqual(self.ctx.posts, [])


class SessionEnvTests(unittest.TestCase):
    def tearDown(self):
        session_env._host_env = None

    def test_host_contextvar_wins_over_process_env(self):
        import os
        os.environ["HERMES_SESSION_ID"] = "from-environ"
        try:
            with support.session_ctx("from-contextvar", "durable-key"):
                self.assertEqual(session_env.session_id(), "from-contextvar")
                self.assertEqual(session_env.session_key(), "durable-key")
                self.assertEqual(session_env.any_session(), "from-contextvar")
        finally:
            del os.environ["HERMES_SESSION_ID"]

    def test_falls_back_to_process_env(self):
        import os
        os.environ["HERMES_SESSION_ID"] = "from-environ"
        try:
            self.assertIsNone(session_env._host_env)
            self.assertEqual(session_env.session_id(), "from-environ")
        finally:
            del os.environ["HERMES_SESSION_ID"]

    def test_empty_without_host_or_env(self):
        self.assertEqual(session_env.session_id(), "")
        self.assertIsNone(session_env.any_session())


if __name__ == "__main__":
    unittest.main()
