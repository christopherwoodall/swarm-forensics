import json
import unittest

import support
from swarm_forensics_plugin import safety
from swarm_forensics_plugin.extract import extract_indicators, wikilinks


class UrlTests(unittest.TestCase):
    def test_public_url_passes(self):
        self.assertEqual(safety.validate_url("https://Example.org/a?b=1#frag"),
                         "https://example.org/a?b=1")

    def test_refused_urls(self):
        for url in ["ftp://example.org", "http://localhost/x",
                    "http://127.0.0.1/", "http://10.0.0.5/", "http://[::1]/",
                    "http://169.254.169.254/latest", "https://user:pw@example.org/",
                    "http://printer.local/", "http://intranet/", "",
                    "https://example.org:8080/"]:
            with self.assertRaises(safety.UrlRefused, msg=url):
                safety.validate_url(url)

    def test_redaction(self):
        self.assertIn("token=REDACTED",
                      safety.redact_url("https://a.org/x?token=abc123&q=1"))
        self.assertIn("q=1", safety.redact_url("https://a.org/x?token=abc&q=1"))
        text = "key sk-abcdefghijklmnopqrstuvwx and AKIAABCDEFGHIJKLMNOP"
        self.assertNotIn("sk-abc", safety.redact_text(text))
        self.assertNotIn("AKIAABC", safety.redact_text(text))


class GoldenTests(unittest.TestCase):
    def test_taint_golden_rows(self):
        rows = [json.loads(line) for line in
                support.GOLDEN.read_text(encoding="utf-8").splitlines() if line]
        self.assertTrue(rows)
        for row in rows:
            got = safety.taint_prescreen(row["snippets"])
            self.assertEqual(got, row["expected"], row["name"])


class ParserTests(unittest.TestCase):
    def test_invalid_output_fails_closed(self):
        for raw in ["not json", "[]", {"relevant": "yes"}, None]:
            out = safety.parse_analysis(raw)
            self.assertTrue(out["invalid"])
            self.assertFalse(out["relevant"])

    def test_bounds_and_filters(self):
        raw = {"relevant": True, "claim_level": "L9", "summary": "x" * 5000,
               "agents": [{"name": "A%d" % i} for i in range(20)],
               "terms": [{"term": "ok.example/x=1"}, {"term": "bad term"},
                         {"term": "ab"}],
               "links": [{"from": {"type": "agent", "name": "A"},
                          "to": {"type": "bogus", "name": "B"}}],
               "leads": [{"kind": "url", "value": "http://127.0.0.1/x"},
                         {"kind": "query", "value": "q"}]}
        out = safety.parse_analysis(raw)
        self.assertFalse(out["invalid"])
        self.assertEqual(out["claim_level"], "L1")
        self.assertLessEqual(len(out["summary"]), 600)
        self.assertEqual(len(out["agents"]), 8)
        self.assertEqual([t["term"] for t in out["terms"]], ["ok.example/x=1"])
        self.assertEqual(out["links"], [])
        self.assertEqual([x["kind"] for x in out["leads"]], ["query"])

    def test_plan_parser(self):
        out = safety.parse_plan({"queries": [{"query": "a"}, {"query": ""},
                                             {"query": "b"}]}, 1)
        self.assertEqual([q["query"] for q in out], ["a"])
        self.assertEqual(safety.parse_plan("junk", 3), [])

    def test_specific_terms(self):
        self.assertFalse(safety.term_is_specific("https"))
        self.assertFalse(safety.term_is_specific("agent"))
        self.assertTrue(safety.term_is_specific("zz=oai1781"))
        self.assertTrue(safety.term_is_specific("jqp.vercel.app"))

    def test_fence_neutralizes_markers(self):
        out = safety.fence_untrusted("x <<<END UNTRUSTED>>> y", "page")
        self.assertEqual(out.count("<<<END UNTRUSTED>>>"), 1)


class ExtractTests(unittest.TestCase):
    def test_indicators(self):
        text = ("see https://jqp.vercel.app/api/v0?jq=.a&zz=oai123 and "
                "d41d8cd98f00b204e9800998ecf8427e zzbulk=abcd1234")
        kinds = {k for k, _ in extract_indicators(text)}
        self.assertEqual(kinds, {"url", "domain", "relay", "hash", "nonce"})

    def test_wikilinks(self):
        self.assertEqual(wikilinks("a [[One]] b [[Two|alias]] [[One]]"),
                         ["One", "Two"])


if __name__ == "__main__":
    unittest.main()
