import unittest

import support
from swarm_forensics_plugin import command, db
from swarm_forensics_plugin import hunt as hunt_mod
from swarm_forensics_plugin.hunt import HuntRefused


def beat(env):
    env.hunts.heartbeat()


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.env.hermes.plan = {"queries": [{"query": "q one"}]}
        self.env.hermes.search_rows = []
        beat(self.env)

    def tearDown(self):
        self.env.close()

    def state(self, hid):
        return self.env.ledger.hunt(hid)["state"]

    def test_start_runs_until_operator_stops(self):
        h = self.env.hunts.start("desktop", "goal")
        self.assertTrue(support.wait_for(
            lambda: self.env.ledger.hunt(h["id"])["cycle"] >= 1))
        self.assertIn(self.state(h["id"]), ("running", "waiting"))
        self.env.hunts.stop(h["id"])
        self.assertTrue(support.wait_for(lambda: self.state(h["id"]) == "stopped"))
        self.assertIsNotNone(self.env.ledger.hunt(h["id"])["ended_utc"])

    def test_one_hunt_at_a_time(self):
        h = self.env.hunts.start("desktop")
        with self.assertRaises(HuntRefused):
            self.env.hunts.start("desktop")
        self.env.hunts.stop(h["id"])
        support.wait_for(lambda: self.state(h["id"]) == "stopped")

    def test_cycle_limit_ends_hunt(self):
        self.env.settings.update({"hunt.cycle_pause_seconds": 5})
        h = self.env.hunts.start("desktop", max_cycles=1)
        self.assertTrue(support.wait_for(lambda: self.state(h["id"]) == "stopped"))
        self.assertEqual(self.env.ledger.hunt(h["id"])["detail"],
                         "cycle limit reached")

    def test_pause_then_human_resume(self):
        h = self.env.hunts.start("desktop")
        support.wait_for(lambda: self.env.ledger.hunt(h["id"])["cycle"] >= 1)
        self.env.hunts.pause(h["id"])
        self.assertTrue(support.wait_for(lambda: self.state(h["id"]) == "paused"))
        self.env.hunts.resume(h["id"])
        self.assertIn(self.state(h["id"]), ("running", "waiting"))
        self.env.hunts.stop(h["id"])
        support.wait_for(lambda: self.state(h["id"]) == "stopped")

    def test_desktop_close_pauses_and_does_not_auto_resume(self):
        self.env.settings.update({"hunt.heartbeat_timeout_seconds": 15})
        h = self.env.hunts.start("desktop")
        support.wait_for(lambda: self.env.ledger.hunt(h["id"])["cycle"] >= 1)
        old = "2000-01-01T00:00:00+00:00"
        self.env.ledger.set_cursor("meta", "desktop_heartbeat", old)
        self.assertTrue(support.wait_for(lambda: self.state(h["id"]) == "paused"))
        self.assertIn("app closed", self.env.ledger.hunt(h["id"])["detail"])
        beat(self.env)  # The app comes back. Nothing resumes by itself.
        self.assertFalse(support.wait_for(
            lambda: self.state(h["id"]) != "paused", timeout=1.5))

    def test_command_origin_ignores_desktop_lease(self):
        self.env.ledger.set_cursor("meta", "desktop_heartbeat",
                                   "2000-01-01T00:00:00+00:00")
        h = self.env.hunts.start("command")
        support.wait_for(lambda: self.env.ledger.hunt(h["id"])["cycle"] >= 1)
        self.assertIn(self.state(h["id"]), ("running", "waiting"))
        self.env.hunts.stop(h["id"])
        support.wait_for(lambda: self.state(h["id"]) == "stopped")

    def test_restart_recovers_as_paused_not_running(self):
        stale = self.env.ledger.create_hunt("desktop", "g")
        self.env.ledger.update_hunt(stale["id"], owner="999:dead",
                                    heartbeat_utc="2000-01-01T00:00:00+00:00")
        self.env.hunts.recover()
        row = self.env.ledger.hunt(stale["id"])
        self.assertEqual(row["state"], "paused")
        self.assertIn("operator restart required", row["detail"])
        self.assertIsNone(self.env.ledger.active_hunt())

    def test_fresh_foreign_lease_blocks_start(self):
        other = self.env.ledger.create_hunt("desktop", "g")
        self.env.ledger.update_hunt(other["id"], owner="999:other",
                                    heartbeat_utc=db.now())
        with self.assertRaises(HuntRefused):
            self.env.hunts.start("desktop")

    def test_global_pause_blocks_start(self):
        self.env.settings.update({"safety.paused": True})
        with self.assertRaises(HuntRefused):
            self.env.hunts.start("desktop")

    def test_blocked_when_capability_missing(self):
        self.env.hermes.search_error = "no search backend"
        self.env.hermes.plan = {"queries": [{"query": "a"}, {"query": "b"},
                                            {"query": "c"}]}
        h = self.env.hunts.start("desktop")
        self.assertTrue(support.wait_for(lambda: self.state(h["id"]) == "blocked"))
        self.assertIn("web failed", self.env.ledger.hunt(h["id"])["detail"])
        self.env.hermes.search_error = None
        self.env.hunts.resume(h["id"])  # A human restarts it.
        self.env.hunts.stop(h["id"])
        support.wait_for(lambda: self.state(h["id"]) == "stopped")


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.env.hermes.plan = {"queries": []}
        beat(self.env)

    def tearDown(self):
        self.env.close()

    def _armed(self):
        sid = self.env.hunts.add_schedule("nightly", "interval", "30m", "goal", 1)
        self.env.hunts.arm_schedule(sid, True)
        with self.env.db.connect() as conn:
            conn.execute("UPDATE schedules SET next_run_utc = ? WHERE id = ?",
                         ("2000-01-01T00:00:00+00:00", sid))
        return sid

    def test_off_by_default_and_needs_master_switch(self):
        self._armed()
        self.assertIsNone(self.env.hunts.tick())

    def test_unarmed_schedule_never_fires(self):
        sid = self._armed()
        self.env.hunts.arm_schedule(sid, False)
        self.env.settings.update({"schedule.enabled": True})
        self.assertIsNone(self.env.hunts.tick())

    def test_armed_schedule_starts_bounded_hunt_only_while_app_open(self):
        sid = self._armed()
        self.env.settings.update({"schedule.enabled": True,
                                  "hunt.heartbeat_timeout_seconds": 15})
        self.env.ledger.set_cursor("meta", "desktop_heartbeat",
                                   "2000-01-01T00:00:00+00:00")
        self.assertIsNone(self.env.hunts.tick())
        beat(self.env)
        started = self.env.hunts.tick()
        self.assertEqual(started["origin"], "schedule")
        self.assertEqual(started["max_cycles"], 1)
        self.assertTrue(support.wait_for(
            lambda: self.env.ledger.hunt(started["id"])["state"] == "stopped"))
        row = [s for s in self.env.hunts.schedules() if s["id"] == sid][0]
        self.assertGreater(row["next_run_utc"], db.now())  # coalesced

    def test_bad_specs_refused(self):
        with self.assertRaises(Exception):
            self.env.hunts.add_schedule("x", "cron", "bad", "g")


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()

        class Svc:
            pass
        self.svc = Svc()
        for name in ("settings", "ledger", "graph", "iocs", "hunts"):
            setattr(self.svc, name, getattr(self.env, name))
        self.env.hermes.plan = {"queries": []}

    def tearDown(self):
        self.env.close()

    def test_help_and_unknown(self):
        self.assertIn("start [goal]", command.handle(self.svc, ""))
        self.assertIn("start [goal]", command.handle(self.svc, "bogus"))

    def test_start_status_stop(self):
        out = command.handle(self.svc, "start find traces")
        self.assertIn("started", out)
        self.assertIn("Hunt", command.handle(self.svc, "status"))
        self.assertIn("Refused", command.handle(self.svc, "start again"))
        self.assertIn("stop requested", command.handle(self.svc, "stop"))
        hid = self.env.ledger.hunts(1)[0]["id"]
        self.assertTrue(support.wait_for(
            lambda: self.env.ledger.hunt(hid)["state"] == "stopped"))

    def test_log_shows_activity_and_start_explains_where_to_look(self):
        out = command.handle(self.svc, "start find traces")
        self.assertIn("/swarm-forensics log", out)
        hid = self.env.ledger.hunts(1)[0]["id"]
        self.env.ledger.event(hid, "search", "web: sample query -> 4 results")
        log = command.handle(self.svc, "log 5")
        self.assertIn("[search] web: sample query -> 4 results", log)
        command.handle(self.svc, "stop")
        self.assertTrue(support.wait_for(
            lambda: self.env.ledger.hunt(hid)["state"] == "stopped"))
        self.assertIn("hunt started", command.handle(self.svc, "log"))

    def test_review_and_decisions(self):
        ioc, _ = self.env.iocs.propose("cmd.example/zz=1")
        self.assertIn("cmd.example", command.handle(self.svc, "review"))
        out = command.handle(self.svc, "accept %d looks right" % ioc["id"])
        self.assertIn("active", out)
        self.assertIn("Refused", command.handle(self.svc, "accept %d" % ioc["id"]))

    def test_settings_roundtrip(self):
        self.assertIn("automatic", command.handle(
            self.svc, "settings iocs.promotion automatic"))
        self.assertIn("Unknown", command.handle(self.svc, "settings nope"))
        out = command.handle(self.svc, "settings safety.exclusion_terms a.b,c.d")
        self.assertIn("a.b", out)


class HuntModuleSanity(unittest.TestCase):
    def test_constants(self):
        self.assertIn("schedule", hunt_mod.DESKTOP_ORIGINS)
        self.assertNotIn("command", hunt_mod.DESKTOP_ORIGINS)


if __name__ == "__main__":
    unittest.main()
