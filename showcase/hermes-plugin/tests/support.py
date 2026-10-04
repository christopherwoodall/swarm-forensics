"""Shared test helpers. Everything runs offline with synthetic data."""

import contextlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "plugins" / "swarm-forensics"
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from swarm_forensics_plugin.db import Database  # noqa: E402
from swarm_forensics_plugin.entities import Graph  # noqa: E402
from swarm_forensics_plugin.hermes import HermesUnavailable  # noqa: E402
from swarm_forensics_plugin.hunt import HuntService  # noqa: E402
from swarm_forensics_plugin.iocs import IocStore  # noqa: E402
from swarm_forensics_plugin.ledger import Ledger  # noqa: E402
from swarm_forensics_plugin.research import Parts  # noqa: E402
from swarm_forensics_plugin.settings import Settings  # noqa: E402

GOLDEN = Path(__file__).resolve().parent / "taint-golden.jsonl"


class FakeHermes:
    """Scripted stand-in for the Hermes runtime."""

    def __init__(self):
        self.search_rows = []
        self.pages = {}
        self.analysis = {"relevant": False}
        self.plan = {"queries": []}
        self.model_error = None
        self.search_error = None
        self.calls = []

    def complete_json(self, system, user, schema_name, settings):
        self.calls.append((schema_name, user))
        if self.model_error:
            raise HermesUnavailable(self.model_error)
        return self.plan if schema_name == "plan" else self.analysis

    def web_search(self, query, limit=10):
        self.calls.append(("search", query))
        if self.search_error:
            raise HermesUnavailable(self.search_error)
        return list(self.search_rows)

    def web_extract(self, urls):
        return [{"url": u, "title": "", "content": self.pages.get(u, "")}
                for u in urls]

    def capabilities(self):
        return {"model": True, "web_search": True, "web_extract": True,
                "detail": []}


def fake_index_getter(rows_by_host=None, status=200):
    """Return a curl_get replacement that serves canned CDX JSON."""
    def getter(url, user_agent, params=None):
        body = json.dumps((rows_by_host or {}).get("default", [])).encode()
        return status, "", body
    return getter


def morphology_card(candidate_id="synthetic-card", excerpt="Synthetic source excerpt."):
    """Return one synthetic candidate card for plugin tests."""
    return {
        "candidate_id": candidate_id,
        "candidate_label": "Synthetic shared-state handoff",
        "status": "possible_new_morphology",
        "summary": "A shared artifact changes before later actions.",
        "evidence": [{"source_ref": "synthetic.jsonl:1", "excerpt": excerpt}],
        "first_observed": "2026-01-01T00:00:00Z",
        "last_observed": "2026-01-02T00:00:00Z",
        "distribution": {"actors": 2, "artifacts": 1},
        "structural_signature": ["write shared state", "later action"],
        "lexical_signature": ["lease refreshed"],
        "nearest_known_morphology": None,
        "similarity_to_known": None,
        "novelty": 0.7,
        "coordination_relevance": 0.8,
        "evidence_strength": "e2",
        "alternative_explanations": ["A central controller may explain the sequence."],
        "missing_evidence": ["No captured read proves later use of the state."],
        "recommended_investigation": ["Search for a later read of the exact artifact."],
        "source_provenance": [{"file": "synthetic.jsonl", "record_id": "r1"}],
    }


class Env:
    """A temp database with every collaborator wired to fakes."""

    def __init__(self, getter=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "test.db")
        self.settings = Settings(self.db)
        self.ledger = Ledger(self.db)
        self.graph = Graph(self.db)
        from swarm_forensics_plugin.registry import Registry
        self.registry = Registry(self.db, self.ledger)
        self.iocs = IocStore(self.db, self.settings)
        self.iocs.seed()
        self.hermes = FakeHermes()
        kwargs = {"getter": getter} if getter else {}
        self.parts = Parts(self.settings, self.ledger, self.graph, self.iocs,
                           self.hermes, registry=self.registry, **kwargs)
        self.hunts = HuntService(self.db, self.parts)
        self.parts.spawner = self.hunts
        self.settings.update({
            "hunt.sources": ["web"], "hunt.cycle_pause_seconds": 5,
            "hunt.request_delay_seconds": 0.5})

    def reset_all_data(self):
        self.hunts.shutdown.set()
        workers = list(getattr(self.hunts, "_workers", {}).values())
        for w in workers:
            if w and w.is_alive():
                w.join(timeout=3)
        self.hunts._workers.clear()
        self.hunts.shutdown.clear()
        self.db.reset()
        self.iocs.seed()
        self.registry.seed()

    def close(self):
        self.hunts.shutdown.set()
        workers = list(getattr(self.hunts, "_workers", {}).values())
        for w in workers:
            if w and w.is_alive():
                w.join(timeout=5)
        self.tmp.cleanup()


@contextlib.contextmanager
def session_ctx(session_id="", session_key=""):
    """Pretend the host bound these session vars for the calling thread."""
    from swarm_forensics_plugin import session_env
    old = session_env._host_env
    def fake(name, default=""):
        return {"HERMES_SESSION_ID": session_id,
                "HERMES_SESSION_KEY": session_key}.get(name, default)
    session_env._host_env = fake
    try:
        yield
    finally:
        session_env._host_env = old


def wait_for(predicate, timeout=10.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(0.05)
    return False


def set_state_dir():
    """Point the plugin at a throwaway state directory."""
    tmp = tempfile.TemporaryDirectory()
    os.environ["SWARM_FORENSICS_STATE_DIR"] = tmp.name
    return tmp
