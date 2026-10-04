"""Unit tests for recursive sub-hunts and hunt trees."""

import unittest

import support
from swarm_forensics_plugin.hunt import HuntRefused


class TestHuntTree(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()

    def tearDown(self):
        self.env.hunts.stop()
        self.env.close()

    def test_spawn_subhunt_hierarchy(self):
        self.env.settings.update({"hunt.max_active_hunts": 5})
        root = self.env.hunts.start("desktop", "Root hunt")
        self.assertEqual(root["depth"], 0)
        self.assertIsNone(root["parent_hunt_id"])

        child1 = self.env.hunts.spawn_subhunt(root["id"], "Child hunt 1")
        self.assertEqual(child1["depth"], 1)
        self.assertEqual(child1["parent_hunt_id"], root["id"])

        child2 = self.env.hunts.spawn_subhunt(child1["id"], "Child hunt 2")
        self.assertEqual(child2["depth"], 2)
        self.assertEqual(child2["parent_hunt_id"], child1["id"])

        child3 = self.env.hunts.spawn_subhunt(child2["id"], "Child hunt 3")
        self.assertEqual(child3["depth"], 3)
        self.assertEqual(child3["parent_hunt_id"], child2["id"])

        children = self.env.ledger.child_hunts(root["id"])
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0]["id"], child1["id"])

    def test_max_depth_exceeded_refused(self):
        self.env.settings.update({"hunt.max_depth": 2})
        root = self.env.hunts.start("desktop", "Root hunt")
        child1 = self.env.hunts.spawn_subhunt(root["id"], "Child 1")
        child2 = self.env.hunts.spawn_subhunt(child1["id"], "Child 2")
        self.assertEqual(child2["depth"], 2)

        with self.assertRaises(HuntRefused) as ctx:
            self.env.hunts.spawn_subhunt(child2["id"], "Child 3")
        self.assertIn("max depth", str(ctx.exception))

    def test_max_concurrent_hunts_refused(self):
        self.env.settings.update({"hunt.max_active_hunts": 2})
        root = self.env.hunts.start("desktop", "Root hunt")
        self.env.hunts.spawn_subhunt(root["id"], "Child 1")

        with self.assertRaises(HuntRefused) as ctx:
            self.env.hunts.spawn_subhunt(root["id"], "Child 2")
        self.assertIn("max concurrent hunts", str(ctx.exception))

    def test_stop_tree(self):
        root = self.env.hunts.start("desktop", "Root hunt")
        child = self.env.hunts.spawn_subhunt(root["id"], "Child 1")
        self.assertEqual(len(self.env.ledger.active_hunts()), 2)

        self.env.hunts.stop(root["id"])
        root_now = self.env.ledger.hunt(root["id"])
        child_now = self.env.ledger.hunt(child["id"])
        self.assertTrue(root_now["stop_requested"] or root_now["state"] == "stopped")
        self.assertTrue(child_now["stop_requested"] or child_now["state"] == "stopped")


if __name__ == "__main__":
    unittest.main()
