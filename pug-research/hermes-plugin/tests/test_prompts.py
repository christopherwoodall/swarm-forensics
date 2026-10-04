import unittest

import support
from swarm_forensics_plugin.prompt_registry import PromptError, PromptRegistry


class PromptRegistryTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.prompts = PromptRegistry(self.env.db)

    def tearDown(self):
        self.env.close()

    def test_default_prompts_seeded(self):
        items = self.prompts.list()
        self.assertGreaterEqual(len(items), 5)
        ids = {p["id"] for p in items}
        self.assertIn("plan_system", ids)
        self.assertIn("plan_user", ids)
        self.assertIn("analyze_system", ids)
        self.assertIn("analyze_user", ids)
        self.assertIn("interactive_agent", ids)
        self.assertIn("hunt_brief", ids)
        self.assertIn("hunt_report", ids)

    def test_get_and_render(self):
        rendered = self.prompts.render(
            "plan_user",
            goal="find beaconing bots",
            limit=5,
            terms="- ioc1\n- ioc2",
            findings="- finding1",
            leads="- lead1",
            past_queries="- q1",
        )
        self.assertIn("Goal: find beaconing bots", rendered)
        self.assertIn("Return at most 5 queries.", rendered)
        self.assertIn("ioc1", rendered)
        self.assertIn("lead1", rendered)

    def test_update_and_reset(self):
        orig = self.prompts.get("plan_system")
        custom_text = "Customized system prompt text."
        updated = self.prompts.update("plan_system", custom_text)
        self.assertEqual(updated["template"], custom_text)
        self.assertEqual(self.prompts.get_template("plan_system"), custom_text)

        # Reset back to default
        reset_item = self.prompts.reset("plan_system")
        self.assertEqual(reset_item["template"], orig["default_template"])
        self.assertEqual(self.prompts.get_template("plan_system"), orig["default_template"])

    def test_export_and_import(self):
        exported = self.prompts.export_all()
        self.assertIn("plan_system", exported)
        import_data = {
            "plan_system": {"template": "Imported plan system template."}
        }
        count = self.prompts.import_all(import_data)
        self.assertEqual(count, 1)
        self.assertEqual(self.prompts.get_template("plan_system"),
                         "Imported plan system template.")

    def test_validation(self):
        with self.assertRaises(PromptError):
            self.prompts.update("plan_system", "")
        with self.assertRaises(PromptError):
            self.prompts.update("non_existent_id", "some text")
        with self.assertRaises(PromptError):
            self.prompts.reset("non_existent_id")
        with self.assertRaises(PromptError):
            self.prompts.import_all("not a dict")


if __name__ == "__main__":
    unittest.main()
