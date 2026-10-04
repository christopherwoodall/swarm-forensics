"""Preserve existing session data when appending morphology storage."""

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

import support  # noqa: F401
from swarm_forensics_plugin import db


class HunterMigrationTests(unittest.TestCase):
    def test_main_migrations_remain_unchanged(self):
        self.assertEqual(len(db.MIGRATIONS), 6)
        self.assertEqual(hashlib.sha256("".join(db.MIGRATIONS[:5]).encode()).hexdigest(),
                         "86eadbebbff0e8e12c3dbe964377e67d7d06aa4d20da1e0f75d80cc994fae96c")

    def test_v5_upgrade_preserves_session_corpus_and_mirror(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "v5.db"
            with sqlite3.connect(path) as conn:
                for migration in db.MIGRATIONS[:5]:
                    conn.executescript(migration)
                conn.execute("PRAGMA user_version = 5")
                conn.execute(
                    "INSERT INTO hunts(id, origin, goal, state, created_utc)"
                    " VALUES ('h1', 'session', 'Synthetic hunt', 'paused', ?)", (db.now(),))
                conn.execute(
                    "INSERT INTO session_bindings(session_id, session_key, hunt_id, bound_utc)"
                    " VALUES ('s1', 'key1', 'h1', ?)", (db.now(),))
                conn.execute(
                    "INSERT INTO corpus_observations(hunt_id, session_id, tool_name,"
                    " query_or_url, observed_utc) VALUES ('h1','s1','web_extract','fixture',?)",
                    (db.now(),))
                conn.execute(
                    "INSERT INTO mirrors(url, sha256, path, fetched_utc)"
                    " VALUES ('https://example.test','synthetic-hash','synthetic-path',?)",
                    (db.now(),))
            migrated = db.Database(path)
            self.assertTrue(path.with_name("v5.db.v5.bak").is_file())
            with migrated.connect() as conn:
                self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 6)
                self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(conn.execute(
                    "SELECT session_key FROM session_bindings WHERE session_id='s1'"
                ).fetchone()[0], "key1")
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM corpus_observations")
                                 .fetchone()[0], 1)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM mirrors").fetchone()[0], 1)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM morphology_candidates")
                                 .fetchone()[0], 0)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM morphology_candidate_log")
                                 .fetchone()[0], 0)
            db.Database(path)
