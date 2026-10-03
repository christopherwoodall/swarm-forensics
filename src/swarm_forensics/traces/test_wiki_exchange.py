"""Offline tests for wiki relay-exchange extraction. No raw archives."""

import unittest

from swarm_forensics.traces.wiki_exchange import (
    EXCHANGE_PATTERN,
    REQUEST_PATTERN,
    RESPONSE_PATTERN,
    added_text,
    request_response_edges,
    url_recurrence_edges,
)


def _rev(body, hunks, **kw):
    rev = {"body": body, "hunks": hunks}
    rev.update(kw)
    return rev


class GrammarTests(unittest.TestCase):
    def test_exchange_pattern_matches_cadence_message(self):
        text = ("Nov16 cohort: MI due task 14:15:59, WV 14:36:35. "
                "Monitoring; will relay. -- SectorAgentNov16OAI")
        self.assertTrue(EXCHANGE_PATTERN.search(text))

    def test_exchange_pattern_ignores_plain_links(self):
        text = "https://api.datausa.io/tesseract/cubes/pums_5 data link"
        self.assertFalse(EXCHANGE_PATTERN.search(text))

    def test_request_response_patterns(self):
        req = "please post STATE5-XX immediately"
        resp = "STATE5-ID confirmed 154074"
        self.assertTrue(REQUEST_PATTERN.search(req))
        self.assertTrue(RESPONSE_PATTERN.search(resp))
        self.assertFalse(REQUEST_PATTERN.search(resp))


class EdgeDetectorTests(unittest.TestCase):
    def _msg(self, time, label, added, page="dse~TestRelay", rev=None):
        return {
            "time": time,
            "label": label,
            "signature": "",
            "page": page,
            "added": added,
            "rev_id": rev or f"{page}@{time}",
        }

    def test_request_then_other_label_response(self):
        msgs = [
            self._msg("2026-06-16T19:38:20Z", "OpenAI-Dec27",
                      "Dec27 cohort: MI due. please post STATE5-XX", rev="r@1"),
            self._msg("2026-06-16T20:46:40Z", "OtherAgent",
                      "STATE5-ID confirmed, values 154074 exact", rev="r@2"),
        ]
        edges = list(request_response_edges(msgs))
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["relation"], "request_then_response_by_other_label")
        self.assertIn("same actor under multiple labels", edges[0]["competing_explanation"])

    def test_request_same_label_no_edge(self):
        msgs = [
            self._msg("2026-06-16T19:38:20Z", "SameAgent",
                      "please post STATE5-XX", rev="r@1"),
            self._msg("2026-06-16T20:46:40Z", "SameAgent",
                      "STATE5-ID confirmed 154074", rev="r@2"),
        ]
        self.assertEqual(list(request_response_edges(msgs)), [])

    def test_url_recurrence_across_labels(self):
        url = "https://la.datausa.io/tesseract-proxy/cubes/pums_5?x=1&y=2"
        msgs = [
            self._msg("2026-06-16T19:57:00Z", "Feb25OAI", f"table at {url}", rev="r@1"),
            self._msg("2026-06-16T20:30:00Z", "Oct10X", f"endpoint: {url}", rev="r@2"),
        ]
        edges = list(url_recurrence_edges(msgs))
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["relation"], "same_specific_url_across_labels")
        self.assertEqual(edges[0]["causal_strength"], "resemblance_only")

    def test_added_text_hunk_extraction(self):
        rev = _rev(
            "old\nnew-line",
            [{"op": "insert", "a0": 1, "a1": 1, "b0": 1, "b1": 2}],
        )
        self.assertEqual(added_text(rev), "new-line")


if __name__ == "__main__":
    unittest.main()
