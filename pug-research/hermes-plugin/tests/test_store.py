import unittest

import support
from swarm_forensics_plugin import db, schedule
from swarm_forensics_plugin.entities import EntityError
from swarm_forensics_plugin.iocs import IocError
from swarm_forensics_plugin.settings import SettingsError


class SchemaAndSettings(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()

    def tearDown(self):
        self.env.close()

    def test_migrate_is_idempotent(self):
        with self.env.db.connect() as conn:
            self.assertEqual(db.migrate(conn), len(db.MIGRATIONS))
            self.assertEqual(db.migrate(conn), len(db.MIGRATIONS))
            self.assertEqual(conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(
                conn.execute("PRAGMA journal_mode").fetchone()[0], "wal")

    def test_defaults_and_updates(self):
        s = self.env.settings
        self.assertEqual(s.get("iocs.promotion"), "manual")
        self.assertFalse(s.get("schedule.enabled"))
        s.update({"iocs.promotion": "automatic", "hunt.max_cycles": 3})
        self.assertEqual(s.get("iocs.promotion"), "automatic")
        self.assertEqual(s.get("hunt.max_cycles"), 3)

    def test_invalid_updates_are_refused_whole(self):
        s = self.env.settings
        with self.assertRaises(SettingsError) as ctx:
            s.update({"iocs.promotion": "yolo", "nope": 1,
                      "hunt.max_cycles": -1, "safety.paused": "yes"})
        self.assertEqual(set(ctx.exception.errors),
                         {"iocs.promotion", "nope", "hunt.max_cycles",
                          "safety.paused"})
        self.assertEqual(s.get("iocs.promotion"), "manual")


class IocTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.iocs = self.env.iocs

    def tearDown(self):
        self.env.close()

    def _evidence(self, n, host="a.example", level="L2", tainted=False):
        ids = []
        for i in range(n):
            eid, _ = self.env.ledger.add_evidence(
                None, "web", "q", "https://%s/p%d" % (host, i), "t",
                "excerpt %s %d" % (host, i), tainted=tainted, claim_level=level)
            ids.append(eid)
        return ids

    def test_seed_loads_once(self):
        self.assertGreater(self.iocs.counts()["active"], 100)
        self.assertEqual(self.iocs.seed(), 0)
        self.assertIn("jqp.vercel.app", self.iocs.active_terms())

    def test_propose_gates(self):
        self.assertEqual(self.iocs.propose("https")[1], "too broad")
        self.env.settings.update({"safety.exclusion_terms": ["bad.example/x1"]})
        self.assertEqual(self.iocs.propose("bad.example/x1")[1], "excluded")
        ioc, reason = self.iocs.propose("new.example/zz=1", "relay", "u")
        self.assertEqual((ioc["status"], reason), ("proposed", "created"))
        self.assertEqual(self.iocs.propose("new.example/zz=1")[1], "existing")

    def test_manual_mode_never_auto_promotes(self):
        ioc, _ = self.iocs.propose("new.example/zz=1")
        for eid in self._evidence(5) + self._evidence(5, host="b.example"):
            self.iocs.propose("new.example/zz=1", evidence_id=eid)
        self.assertEqual(self.iocs.apply_policy(), [])
        self.assertEqual(self.iocs.detail(ioc["id"])["status"], "proposed")

    def test_automatic_rules(self):
        self.env.settings.update({"iocs.promotion": "automatic"})
        good, _ = self.iocs.propose("good.example/zz=1")
        thin, _ = self.iocs.propose("thin.example/zz=2")
        tainted, _ = self.iocs.propose("taint.example/zz=3")
        for host in ("a.example", "b.example"):
            for eid in self._evidence(2, host):
                self.iocs.propose("good.example/zz=1", evidence_id=eid)
        for eid in self._evidence(1, "c.example"):
            self.iocs.propose("thin.example/zz=2", evidence_id=eid)
        for host in ("d.example", "e.example"):
            for eid in self._evidence(2, host, tainted=True):
                self.iocs.propose("taint.example/zz=3", evidence_id=eid)
        self.assertEqual(self.iocs.apply_policy(), ["good.example/zz=1"])
        self.assertEqual(self.iocs.detail(thin["id"])["status"], "proposed")
        self.assertEqual(self.iocs.detail(tainted["id"])["status"], "proposed")
        log = self.iocs.detail(good["id"])["log"][-1]
        self.assertEqual(log["actor"], "policy")
        self.assertIn("auto:", log["reason"])

    def test_daily_cap(self):
        self.env.settings.update({"iocs.promotion": "automatic",
                                  "iocs.auto_max_per_day": 1})
        for n in range(2):
            term = "cap%d.example/zz=1" % n
            self.iocs.propose(term)
            for host in ("a.example", "b.example"):
                for eid in self._evidence(2, "%d%s" % (n, host)):
                    self.iocs.propose(term, evidence_id=eid)
        self.assertEqual(len(self.iocs.apply_policy()), 1)

    def test_human_rejection_is_final_for_policy(self):
        self.env.settings.update({"iocs.promotion": "automatic"})
        ioc, _ = self.iocs.propose("rej.example/zz=1")
        self.iocs.decide(ioc["id"], "reject", "noise")
        for host in ("a.example", "b.example"):
            for eid in self._evidence(2, "r" + host):
                self.iocs.propose("rej.example/zz=1", evidence_id=eid)
        self.assertEqual(self.iocs.apply_policy(), [])
        self.assertEqual(self.iocs.detail(ioc["id"])["status"], "rejected")
        with self.assertRaises(IocError):
            self.iocs.transition(ioc["id"], "active", "policy")

    def test_decisions_and_narrow(self):
        ioc, _ = self.iocs.propose("wide.example/county.json")
        out = self.iocs.decide(ioc["id"], "narrow", "why",
                               narrower="wide.example/county.json+jqp.vercel.app")
        self.assertEqual(out["status"], "active")
        self.assertEqual(self.iocs.detail(ioc["id"])["status"], "rejected")
        with self.assertRaises(IocError):
            self.iocs.decide(ioc["id"], "narrow", narrower="https")
        self.iocs.decide(out["id"], "deactivate", "stale")
        self.assertEqual(self.iocs.detail(out["id"])["status"], "inactive")
        self.assertEqual(len(self.iocs.detail(out["id"])["log"]), 3)


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.g = self.env.graph

    def tearDown(self):
        self.env.close()

    def test_upsert_never_erases_and_merges(self):
        a = self.g.upsert("agent", "Scout-7", "first", {"k": 1})
        b = self.g.upsert("agent", "scout-7", "second", {"j": 2})
        self.assertEqual(a["id"], b["id"])
        self.assertEqual(b["summary"], "first")
        self.assertEqual(b["attrs"], {"k": 1, "j": 2})

    def test_wikilinks_make_backlinks(self):
        agent = self.g.upsert("agent", "Scout-7")
        swarm = self.g.upsert("swarm", "Blue Fleet")
        self.g.update(swarm["id"], notes="Led by [[Scout-7]] and [[Ghost]].")
        view_agent = self.g.view(agent["id"])
        self.assertEqual([b["name"] for b in view_agent["backlinks"]],
                         ["Blue Fleet"])
        self.assertEqual(self.g.view(swarm["id"])["unresolved"], ["Ghost"])
        self.g.update(swarm["id"], notes="No links now.")
        self.assertEqual(self.g.view(agent["id"])["backlinks"], [])

    def test_graph_neighborhood_and_cascade(self):
        a = self.g.upsert("agent", "A")
        b = self.g.upsert("swarm", "B")
        c = self.g.upsert("case", "C")
        d = self.g.upsert("case", "D")
        self.g.link(a["id"], b["id"], "member_of")
        self.g.link(b["id"], c["id"], "part_of")
        near = self.g.graph(center=a["id"], depth=1)
        self.assertEqual({n["name"] for n in near["nodes"]}, {"A", "B"})
        wide = self.g.graph(center=a["id"], depth=2)
        self.assertEqual({n["name"] for n in wide["nodes"]}, {"A", "B", "C"})
        self.assertNotIn(d["id"], {n["id"] for n in wide["nodes"]})
        self.g.delete(b["id"])
        self.assertEqual(self.g.graph()["edges"], [])

    def test_validation(self):
        with self.assertRaises(EntityError):
            self.g.upsert("person", "X")
        with self.assertRaises(EntityError):
            self.g.upsert("agent", "bad [name]")
        a = self.g.upsert("agent", "A")
        with self.assertRaises(EntityError):
            self.g.link(a["id"], a["id"], "related")
        with self.assertRaises(EntityError):
            self.g.link(a["id"], "missing", "related")

    def test_sql_injection_is_inert(self):
        self.g.upsert("agent", "A")
        self.assertEqual(self.g.list(query="x' OR '1'='1"), [])
        self.assertEqual(len(self.g.list()), 1)


class ScheduleSpecs(unittest.TestCase):
    def test_interval(self):
        self.assertEqual(schedule.parse_interval("6h"), 21600)
        for bad in ("1m", "x", "10s", "0h"):
            with self.assertRaises(schedule.ScheduleError):
                schedule.parse_interval(bad)

    def test_cron_next(self):
        from datetime import datetime, timezone
        start = datetime(2026, 1, 1, 10, 7, tzinfo=timezone.utc)
        nxt = schedule.next_after("cron", "*/15 * * * *", start)
        self.assertEqual((nxt.hour, nxt.minute), (10, 15))
        nxt = schedule.next_after("cron", "30 2 * * *", start)
        self.assertEqual((nxt.day, nxt.hour, nxt.minute), (2, 2, 30))
        for bad in ("* * *", "61 * * * *", "a b c d e"):
            with self.assertRaises(schedule.ScheduleError):
                schedule.validate("cron", bad)


if __name__ == "__main__":
    unittest.main()
