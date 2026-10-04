"""Research engine: one hunt cycle.

plan -> search -> sweep -> read -> analyze -> record -> revise.

The model plans queries and reads evidence. It only proposes. Policy and
the operator decide what becomes an IOC. Fetched text is data. Every
step honors the stop flag, so an operator can end a hunt at once.
"""

from urllib.parse import urlsplit

from . import prompts
from .db import now
from .extract import extract_indicators
from .hermes import HermesUnavailable
from .predict import generate_candidates
from .safety import (
    CLAIM_LEVELS,
    UrlRefused,
    fence_untrusted,
    host_of,
    parse_analysis,
    parse_plan,
    taint_prescreen,
    validate_url,
)
from .sources import INDEX_SOURCES, IndexSources, curl_get

TERMS_PER_SOURCE = 6
PROMPT_TERMS = 30
HIT_BATCH = 20
MAX_FAILURES = 3


def _short(text, limit):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


class Blocked(RuntimeError):
    """A capability is missing for good. The hunt waits for the operator."""


class Parts:
    """The collaborators the engine needs."""

    def __init__(self, settings, ledger, graph, iocs, hermes, getter=curl_get):
        self.getter = getter
        self.settings = settings
        self.ledger = ledger
        self.graph = graph
        self.iocs = iocs
        self.hermes = hermes


class Engine:
    def __init__(self, parts, ctl):
        """`ctl` provides stopped() and wait(seconds) -> True when stopping."""
        self.p = parts
        self.ctl = ctl
        self.failures = {"model": 0, "web": 0}

    # -- one cycle ----------------------------------------------------------

    def run_cycle(self, hunt):
        cfg = self.p.settings.all()
        totals = {"queries": 0, "pages": 0, "evidence": 0, "entities": 0,
                  "terms": 0, "promoted": 0, "throttled": 0}
        hid = hunt["id"]
        goal = hunt["goal"] or cfg["hunt.default_goal"]
        sources = cfg["hunt.sources"]
        if not self.p.ledger.totals()["candidates"]:
            self.p.ledger.add_candidates(generate_candidates())
        pages = []
        if "web" in sources:
            pages = self._search(hid, goal, cfg, totals)
        if self.ctl.stopped():
            return totals
        self._sweep(hid, goal, cfg, totals)
        if self.ctl.stopped():
            return totals
        self._read(hid, goal, cfg, pages, totals)
        promoted = self.p.iocs.apply_policy()
        totals["promoted"] = len(promoted)
        for term in promoted:
            self.p.ledger.event(hid, "promotion", "auto-promoted %s" % term,
                                data={"term": term})
        return totals

    # -- planning and search --------------------------------------------------

    def _slice_terms(self, key, size):
        terms = self.p.iocs.active_terms()
        if not terms:
            return []
        start = int(self.p.ledger.cursor("plan", key, "0")) % len(terms)
        picked = [terms[(start + i) % len(terms)] for i in range(min(size, len(terms)))]
        self.p.ledger.set_cursor("plan", key, (start + size) % len(terms))
        return picked

    def _plan(self, hid, goal, cfg):
        limit = cfg["hunt.max_queries_per_cycle"]
        leads = self.p.ledger.open_leads("query", limit)
        if cfg["hunt.use_model"] and self.failures["model"] < MAX_FAILURES:
            try:
                raw = self.p.hermes.complete_json(
                    prompts.PLAN_SYSTEM,
                    prompts.plan_user(
                        goal, self._slice_terms("prompt", PROMPT_TERMS),
                        self.p.ledger.recent_findings(),
                        self.p.ledger.recent_queries(), leads, limit),
                    "plan", cfg)
                self.failures["model"] = 0
                plan = [q["query"] for q in parse_plan(raw, limit)]
                if plan:
                    return plan, leads
            except HermesUnavailable as exc:
                self._fail(hid, "model", exc)
        picked = self._slice_terms("web", limit)
        queries = [lead["value"] for lead in leads]
        queries += ['"%s"' % t for t in picked]
        return queries[:limit], leads

    def _fail(self, hid, kind, exc):
        self.failures[kind] += 1
        self.p.ledger.event(hid, "warn", "%s unavailable: %s" % (kind, exc),
                            level="warn")
        if self.failures[kind] >= MAX_FAILURES:
            raise Blocked("%s failed %d times in a row: %s"
                          % (kind, MAX_FAILURES, exc))

    def _say(self, hid, kind, message, level="info", data=None):
        """Write one line the operator can follow in the activity feed."""
        self.p.ledger.event(hid, kind, message, level=level, data=data)

    def _search(self, hid, goal, cfg, totals):
        queries, leads = self._plan(hid, goal, cfg)
        self._say(hid, "plan", "planned %d web queries: %s" % (
            len(queries), " | ".join(_short(q, 70) for q in queries[:6]) or "none"))
        lead_by_value = {lead["value"]: lead for lead in leads}
        found, seen = [], set()
        for query in queries:
            if self.ctl.stopped():
                break
            if self.p.ledger.query_seen("web", query):
                continue
            try:
                rows = self.p.hermes.web_search(
                    query, min(10, cfg["hunt.max_results_per_query"]))
            except HermesUnavailable as exc:
                self.p.ledger.log_query(hid, "web", query, "error")
                self._fail(hid, "web", exc)
                continue
            self.failures["web"] = 0
            self.p.ledger.log_query(hid, "web", query, "ok", 200, len(rows))
            totals["queries"] += 1
            self._say(hid, "search", "web: %s -> %d results" % (_short(query, 90), len(rows)))
            if query in lead_by_value:
                self.p.ledger.close_lead(lead_by_value[query]["id"])
            for row in rows:
                try:
                    url = validate_url(row["url"])
                except UrlRefused:
                    continue
                if url in seen or self.p.ledger.url_known(url) or \
                        self.p.ledger.query_seen("page", url, 24 * 7):
                    continue
                seen.add(url)
                found.append(dict(row, url=url, query=query))
            if self.ctl.wait(cfg["hunt.request_delay_seconds"]):
                break
        return found[:cfg["hunt.max_pages_per_cycle"]]

    # -- index sweeps -----------------------------------------------------------

    def _sweep(self, hid, goal, cfg, totals):
        index = IndexSources("swarm-forensics/1.0", cfg["hunt.request_delay_seconds"],
                             cfg["hunt.max_results_per_query"], self.ctl.wait,
                             self.p.getter)
        for source in [s for s in cfg["hunt.sources"] if s in INDEX_SOURCES]:
            terms = self._slice_terms("idx-" + source, TERMS_PER_SOURCE)
            since = self.p.ledger.cursor(source, "since")
            queries = index.queries_for(source, terms, since) if terms else []
            clean = bool(queries)
            ran = found = 0
            failed = {}
            for query in queries:
                if self.ctl.stopped():
                    return
                label = query["id"]
                if self.p.ledger.query_seen(source, label, 6):
                    continue
                outcome, status, hits = index.run(source, query)
                if outcome == "aborted":
                    return
                self.p.ledger.log_query(hid, source, label, outcome, status,
                                        len(hits))
                totals["queries"] += 1
                ran += 1
                found += len(hits)
                if outcome == "throttled":
                    totals["throttled"] += 1
                    clean = False
                    self._say(hid, "throttle",
                              "%s throttled (HTTP %s); not a negative" % (source, status),
                              level="warn")
                elif outcome == "error":
                    clean = False
                    failed[status] = failed.get(status, 0) + 1
                if hits:
                    self._record_hits(hid, goal, cfg, source, label, hits, totals)
            if failed:
                self._say(hid, "sweep", "%s: %d of %d queries failed (HTTP %s). Not counted"
                          " as negatives." % (source, sum(failed.values()), ran,
                                              ", ".join(str(s) for s in sorted(failed))),
                          level="warn")
            elif ran:
                self._say(hid, "sweep", "%s: %d queries, %d hits" % (source, ran, found))
            if clean:
                self.p.ledger.set_cursor(source, "since", now()[:10])
        if "cdx" in cfg["hunt.sources"]:
            for cand in self.p.ledger.unprobed_candidates(3):
                if self.ctl.stopped():
                    return
                outcome, status, hits = index.run(
                    "cdx", index.candidate_query(cand["url"]))
                if outcome in ("ok",):
                    self.p.ledger.mark_candidate(cand["id"], len(hits))
                    if hits:
                        self._record_hits(hid, goal, cfg, "cdx", "candidate",
                                          hits, totals)
                self.p.ledger.log_query(hid, "cdx", "cand:" + cand["url"][:200],
                                        outcome, status, len(hits))

    def _record_hits(self, hid, goal, cfg, source, label, hits, totals):
        ids = []
        for hit in hits:
            tainted = taint_prescreen([hit["url"], hit["excerpt"]])
            eid, created = self.p.ledger.add_evidence(
                hid, source, label, hit["url"], hit["title"], hit["excerpt"],
                tainted=tainted)
            if created:
                ids.append(eid)
                totals["evidence"] += 1
        if not ids or not cfg["hunt.use_model"] or \
                self.failures["model"] >= MAX_FAILURES:
            return
        listing = "\n".join(h["url"] for h in hits[:HIT_BATCH])
        analysis = self._analyze(
            hid, goal, cfg, listing, "Observed request URLs from %s" % source)
        if analysis["relevant"]:
            self._apply(hid, cfg, analysis, ids[:5], source, label, "", listing,
                        totals, tainted=taint_prescreen([listing]))

    # -- reading pages ----------------------------------------------------------

    def _read(self, hid, goal, cfg, pages, totals):
        texts = {}
        if cfg["hunt.fetch_pages"] and pages:
            for i in range(0, len(pages), 5):
                if self.ctl.stopped():
                    return
                batch = [p["url"] for p in pages[i:i + 5]]
                try:
                    for row in self.p.hermes.web_extract(batch):
                        texts[row["url"]] = row["content"]
                except HermesUnavailable as exc:
                    self.p.ledger.event(hid, "warn", "page read failed: %s" % exc,
                                        level="warn")
        for page in pages:
            if self.ctl.stopped():
                return
            text = texts.get(page["url"]) or page.get("description", "")
            totals["pages"] += 1
            self.p.ledger.log_query(hid, "page", page["url"], "ok", 200, 0)
            if not text.strip():
                self._say(hid, "page", "empty page: %s" % _short(page["url"], 90))
                continue
            tainted = taint_prescreen([text])
            analysis = self._analyze(
                hid, goal, cfg, text,
                "Page %s (%s)" % (page["url"], page.get("title", "")))
            if not analysis["relevant"]:
                self._say(hid, "page", "not relevant: %s" % _short(page["url"], 90))
                continue
            self._say(hid, "page", "relevant (%s%s): %s" % (
                analysis["claim_level"], ", tainted" if tainted else "",
                _short(analysis["summary"] or page["url"], 120)))
            eid, created = self.p.ledger.add_evidence(
                hid, "web", page["query"], page["url"], page.get("title", ""),
                self._excerpt(analysis, text), tainted=tainted,
                claim_level=analysis["claim_level"], analysis=analysis)
            if created:
                totals["evidence"] += 1
                self._apply(hid, cfg, analysis, [eid], "web", page["query"],
                            page.get("title", ""), text, totals, tainted,
                            page["url"])

    @staticmethod
    def _excerpt(analysis, text):
        return (analysis["summary"] + "\n" + " ".join(text.split())[:600]).strip()

    # -- analysis -----------------------------------------------------------------

    def _analyze(self, hid, goal, cfg, text, label):
        if cfg["hunt.use_model"] and self.failures["model"] < MAX_FAILURES:
            try:
                raw = self.p.hermes.complete_json(
                    prompts.ANALYZE_SYSTEM,
                    "Hunt goal: %s\n%s" % (goal, fence_untrusted(text, label)),
                    "analysis", cfg)
                self.failures["model"] = 0
                analysis = parse_analysis(raw)
                if analysis["invalid"]:
                    self.p.ledger.event(hid, "warn", "model analysis was invalid",
                                        level="warn")
                return analysis
            except HermesUnavailable as exc:
                self._fail(hid, "model", exc)
        return self._heuristic(text)

    def _heuristic(self, text):
        """No-model analysis: match the page against active IOC terms."""
        lower = text.lower()
        matches = [t for t in self.p.iocs.active_terms() if t.lower() in lower]
        empty = parse_analysis({"relevant": False})
        if not matches:
            return dict(empty, invalid=False)
        level = "L2" if len(matches) >= 3 else "L1"
        out = dict(empty, invalid=False, relevant=True, claim_level=level)
        out["summary"] = "Matched %d active indicators: %s" % (
            len(matches), ", ".join(matches[:5]))
        return out

    # -- recording ----------------------------------------------------------------

    def _apply(self, hid, cfg, analysis, evidence_ids, source, query, title, text,
               totals, tainted, url=""):
        eid = evidence_ids[0]
        level = analysis["claim_level"]
        graph_on = cfg["graph.auto_entities"]
        made = {}
        if graph_on:
            for kind in ("agent", "swarm", "case"):
                for item in analysis[kind + "s"]:
                    made[(kind, item["name"])] = self._entity(
                        kind, item["name"], item["description"], eid, totals)
            for link in analysis["links"]:
                ends = []
                for end in (link["from"], link["to"]):
                    key = (end["type"], end["name"])
                    if key not in made:
                        made[key] = self._entity(end["type"], end["name"], "",
                                                 eid, totals)
                    ends.append(made[key])
                if all(ends) and ends[0] != ends[1]:
                    self.p.graph.link(ends[0], ends[1], link["kind"], eid)
            if CLAIM_LEVELS.index(level) >= 1 and (url or title):
                label = (title or host_of(url) or "trace")[:100]
                trace = self._entity("trace", label, analysis["summary"][:300],
                                     eid, totals, {"url": url, "claim_level": level})
                if trace:
                    for kind, value in extract_indicators(text)[:40]:
                        self.p.graph.add_indicator(trace, kind, value, eid)
                    for (kind, _), entity_id in made.items():
                        if kind in ("agent", "swarm") and entity_id:
                            self.p.graph.link(trace, entity_id, "trace_of", eid)
        confidence = 0.2 * (CLAIM_LEVELS.index(level) + 1)
        for item in analysis["terms"]:
            ioc, reason = None, ""
            for evidence_id in evidence_ids:
                ioc, reason = self.p.iocs.propose(
                    item["term"], item["category"], provenance=url or source,
                    evidence_id=evidence_id, confidence=confidence,
                    note=item["why"])
            if ioc and reason == "created":
                totals["terms"] += 1
        for lead in analysis["leads"]:
            self.p.ledger.add_lead(lead["kind"], lead["value"], confidence,
                                   hunt_id=hid)
        if CLAIM_LEVELS.index(level) >= CLAIM_LEVELS.index(
                cfg["safety.alert_on_claim_level"]):
            self.p.ledger.event(
                hid, "alert", "%s finding: %s" % (level, analysis["summary"][:200]),
                level="alert", data={"evidence_id": eid, "tainted": tainted,
                                     "host": urlsplit(url).hostname or source})

    def _entity(self, kind, name, description, evidence_id, totals, attrs=None):
        try:
            existed = self.p.graph.find(kind, name) is not None
            entity = self.p.graph.upsert(kind, name, description, attrs,
                                         evidence_id=evidence_id)
        except ValueError:
            return None
        if not existed:
            totals["entities"] += 1
        return entity["id"]
