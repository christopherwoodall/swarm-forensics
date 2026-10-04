import unittest

import support
from swarm_forensics_plugin.url_store import UrlError, UrlStore


class UrlStoreTests(unittest.TestCase):
    def setUp(self):
        self.env = support.Env()
        self.urls = UrlStore(self.env.db)

    def tearDown(self):
        self.env.close()

    def test_add_and_list(self):
        row = self.urls.add("https://malicious.example.com/c2/beacon?id=1",
                            source="evidence")
        self.assertEqual(row["host"], "malicious.example.com")
        self.assertEqual(row["status"], "discovered")

        items = self.urls.list()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["host"], "malicious.example.com")

    def test_triage_benign_and_is_benign(self):
        url = "https://safe-cdn.example.org/bundles/app.js"
        self.urls.add(url)
        self.assertFalse(self.urls.is_benign(url))
        self.assertFalse(self.urls.is_benign("safe-cdn.example.org"))

        # Mark as benign
        triaged = self.urls.triage(url, "benign", reason="whitelisted CDN asset")
        self.assertEqual(triaged["status"], "benign")
        self.assertEqual(triaged["reason"], "whitelisted CDN asset")

        self.assertTrue(self.urls.is_benign(url))
        self.assertTrue(self.urls.is_benign("safe-cdn.example.org"))
        self.assertFalse(self.urls.is_benign("https://other.example.com"))

    def test_counts(self):
        self.urls.add("https://a.example/1", status="discovered")
        self.urls.add("https://b.example/2", status="examined")
        self.urls.add("https://c.example/3", status="benign")
        self.urls.add("https://d.example/4", status="suspicious")

        counts = self.urls.counts()
        self.assertEqual(counts["discovered"], 1)
        self.assertEqual(counts["examined"], 1)
        self.assertEqual(counts["benign"], 1)
        self.assertEqual(counts["suspicious"], 1)

    def test_validation(self):
        with self.assertRaises(UrlError):
            self.urls.add("")
        with self.assertRaises(UrlError):
            self.urls.add("https://example.com", status="invalid_status")
        with self.assertRaises(UrlError):
            self.urls.triage("https://example.com", "unknown_verdict")


if __name__ == "__main__":
    unittest.main()
