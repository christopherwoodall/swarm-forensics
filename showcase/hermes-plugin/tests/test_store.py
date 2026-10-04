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

    def test_v1_to_v2_migration(self):
        import sqlite3
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "v1.db"
            conn = sqlite3.connect(db_file)
            conn.executescript(db.MIGRATIONS[0])
            conn.execute("PRAGMA user_version = 1")
            stamp = db.now()
            conn.execute("INSERT INTO entities(id, type, name, origin, created_utc, updated_utc)"
                         " VALUES ('e_trace', 'trace', 'Trace1', 'human', ?, ?)", (stamp, stamp))
            conn.execute("INSERT INTO entities(id, type, name, origin, created_utc, updated_utc)"
                         " VALUES ('e_case', 'case', 'Case1', 'human', ?, ?)", (stamp, stamp))
            conn.execute("INSERT INTO entities(id, type, name, origin, created_utc, updated_utc)"
                         " VALUES ('e_agent', 'agent', 'Agent1', 'human', ?, ?)", (stamp, stamp))
            conn.execute("INSERT INTO links(src, dst, kind, created_utc)"
                         " VALUES ('e_trace', 'e_agent', 'trace_of', ?)", (stamp,))
            conn.execute("INSERT INTO links(src, dst, kind, created_utc)"
                         " VALUES ('e_agent', 'e_case', 'member_of', ?)", (stamp,))
            conn.execute("INSERT INTO indicators(entity_id, kind, value, first_seen_utc)"
                         " VALUES ('e_trace', 'ip', '1.2.3.4', ?)", (stamp,))
            conn.commit()
            conn.close()

            # Open via Database, triggering backup and migration
            migrated_db = db.Database(db_file)
            bak_file = db_file.with_name(db_file.name + ".v1.bak")
            self.assertTrue(bak_file.exists())

            with migrated_db.connect() as c:
                ver = c.execute("PRAGMA user_version").fetchone()[0]
                self.assertEqual(ver, 5)
                fk_violations = c.execute("PRAGMA foreign_key_check").fetchall()
                self.assertEqual(fk_violations, [])

                q_trace = "SELECT type, name, tags FROM entities WHERE id = 'e_trace'"
                row_trace = c.execute(q_trace).fetchone()
                self.assertEqual(row_trace["type"], "artifact")
                self.assertEqual(row_trace["tags"], "[]")
                q_case = "SELECT type, name FROM entities WHERE id = 'e_case'"
                row_case = c.execute(q_case).fetchone()
                self.assertEqual(row_case["type"], "campaign")

                links = c.execute("SELECT src, dst, kind FROM links").fetchall()
                self.assertEqual(len(links), 2)
                for lnk in links:
                    self.assertEqual(lnk["kind"], "part_of")

                ind = c.execute("SELECT entity_id, kind, value FROM indicators").fetchone()
                self.assertEqual(ind["entity_id"], "e_trace")
                self.assertEqual(ind["value"], "1.2.3.4")

                # Verify new tables exist
                self.assertIsNotNone(c.execute("SELECT 1 FROM index_sources").fetchall())
                self.assertIsNotNone(c.execute("SELECT 1 FROM url_grammar").fetchall())
                self.assertIsNotNone(c.execute("SELECT 1 FROM prompts").fetchall())
                self.assertIsNotNone(c.execute("SELECT 1 FROM urls").fetchall())

    def test_v2_to_v3_migration(self):
        import sqlite3
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "v2.db"
            conn = sqlite3.connect(db_file)
            conn.executescript(db.MIGRATIONS[0])
            conn.executescript(db.MIGRATIONS[1])
            conn.execute("PRAGMA user_version = 2")
            stamp = db.now()
            conn.execute("INSERT INTO entities(id, type, name, origin, created_utc, updated_utc)"
                         " VALUES ('e1', 'artifact', 'Artifact1', 'human', ?, ?)", (stamp, stamp))
            conn.execute("INSERT INTO iocs(term, category, status, origin, added_utc, updated_utc)"
                         " VALUES ('sample.ioc', 'relay', 'active', 'human', ?, ?)", (stamp, stamp))
            conn.commit()
            conn.close()

            migrated = db.Database(db_file)
            bak = db_file.with_name(db_file.name + ".v2.bak")
            self.assertTrue(bak.exists())

            with migrated.connect() as c:
                self.assertEqual(c.execute("PRAGMA user_version").fetchone()[0], 5)
                self.assertEqual(c.execute("PRAGMA foreign_key_check").fetchall(), [])
                # Entity has tags column
                row = c.execute("SELECT tags FROM entities WHERE id = 'e1'").fetchone()
                self.assertEqual(row["tags"], "[]")
                # Benign status can be written to iocs
                c.execute("UPDATE iocs SET status = 'benign' WHERE term = 'sample.ioc'")
                ioc_row = c.execute("SELECT status FROM iocs WHERE term = 'sample.ioc'").fetchone()
                self.assertEqual(ioc_row["status"], "benign")
                # Prompts and urls tables exist
                self.assertEqual(c.execute("SELECT COUNT(*) FROM prompts").fetchone()[0], 0)
                self.assertEqual(c.execute("SELECT COUNT(*) FROM urls").fetchone()[0], 0)

    def test_v3_to_v4_migration(self):
        import sqlite3
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "v3.db"
            conn = sqlite3.connect(db_file)
            for m in db.MIGRATIONS[:3]:
                conn.executescript(m)
            conn.execute("PRAGMA user_version = 3")
            stamp = db.now()
            conn.execute(
                "INSERT INTO hunts("
                "id, origin, goal, state, created_utc, started_utc, heartbeat_utc)"
                " VALUES ('h1', 'desktop', 'find traces', 'running', ?, ?, ?)",
                (stamp, stamp, stamp))
            conn.commit()
            conn.close()

            migrated = db.Database(db_file)
            bak = db_file.with_name(db_file.name + ".v3.bak")
            self.assertTrue(bak.exists())

            with migrated.connect() as c:
                self.assertEqual(c.execute("PRAGMA user_version").fetchone()[0], 5)
                self.assertEqual(c.execute("PRAGMA foreign_key_check").fetchall(), [])
                query = "SELECT parent_hunt_id, depth, session_id FROM hunts WHERE id = 'h1'"
                row = c.execute(query).fetchone()
                self.assertIsNone(row["parent_hunt_id"])
                self.assertEqual(row["depth"], 0)
                self.assertIsNone(row["session_id"])

    def test_v4_to_v5_migration(self):
        import sqlite3
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "v4.db"
            conn = sqlite3.connect(db_file)
            for m in db.MIGRATIONS[:4]:
                conn.executescript(m)
            conn.execute("PRAGMA user_version = 4")
            stamp = db.now()
            conn.execute(
                "INSERT INTO hunts("
                "id, origin, goal, state, created_utc, started_utc, heartbeat_utc)"
                " VALUES ('h1', 'desktop', 'find traces', 'running', ?, ?, ?)",
                (stamp, stamp, stamp))
            conn.commit()
            conn.close()

            migrated = db.Database(db_file)
            bak = db_file.with_name(db_file.name + ".v4.bak")
            self.assertTrue(bak.exists())

            with migrated.connect() as c:
                self.assertEqual(c.execute("PRAGMA user_version").fetchone()[0], 5)
                self.assertEqual(c.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertIsNotNone(c.execute("SELECT 1 FROM session_bindings").fetchall())
                self.assertIsNotNone(c.execute("SELECT 1 FROM corpus_observations").fetchall())
                self.assertIsNotNone(c.execute("SELECT 1 FROM mirrors").fetchall())

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

    def test_part_of_direction_flip_and_parents_children(self):
        agent = self.g.upsert("agent", "AgentAlpha")
        artifact = self.g.upsert("artifact", "Page1")
        # Try linking agent -> artifact with part_of (upside-down).
        # Should be flipped so artifact is src and agent is dst.
        link_id = self.g.link(agent["id"], artifact["id"], "part_of")
        with self.env.db.connect() as conn:
            q = "SELECT src, dst, kind FROM links WHERE id = ?"
            row = conn.execute(q, (link_id,)).fetchone()
            self.assertEqual(row["src"], artifact["id"])
            self.assertEqual(row["dst"], agent["id"])
            self.assertEqual(row["kind"], "part_of")

        # Same rank (agent -> agent) with part_of becomes related
        agent2 = self.g.upsert("agent", "AgentBeta")
        link_same = self.g.link(agent["id"], agent2["id"], "part_of")
        with self.env.db.connect() as conn:
            row_same = conn.execute(
                "SELECT kind FROM links WHERE id = ?", (link_same,)
            ).fetchone()
            self.assertEqual(row_same["kind"], "related")

        # View check for parents and children
        view_agent = self.g.view(agent["id"])
        self.assertIn("artifact", view_agent["children"])
        self.assertEqual(len(view_agent["children"]["artifact"]), 1)
        self.assertEqual(view_agent["children"]["artifact"][0]["name"], "Page1")

        view_artifact = self.g.view(artifact["id"])
        self.assertIn("agent", view_artifact["parents"])
        self.assertEqual(len(view_artifact["parents"]["agent"]), 1)
        self.assertEqual(view_artifact["parents"]["agent"][0]["name"], "AgentAlpha")


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
