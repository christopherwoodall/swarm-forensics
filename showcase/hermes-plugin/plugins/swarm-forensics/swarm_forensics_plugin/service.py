"""Service: wires storage, policy, research, and lifecycle together.

One service per process. The desktop API, the `/swarm-forensics` command,
and the scheduler all call the same object, so they see the same state.
"""

import threading

from .dataset_hunter import DatasetHunter
from .dataset_probes import DatasetError
from .db import Database
from .entities import Graph
from .hermes import HermesRuntime
from .hunt import HuntService
from .iocs import IocStore
from .ledger import Ledger
from .mirror import MirrorStore
from .narration import Narrator
from .paths import PLUGIN_ID, db_path, state_dir
from .prompt_registry import PromptRegistry
from .registry import Registry
from .research import Parts
from .settings import SCHEMA_VERSION, Settings
from .url_store import UrlStore


def _broadcast(event, payload):
    """Push an event to connected desktop windows. Best effort."""
    try:
        from hermes_cli.plugin_events import broadcast_plugin_event
        broadcast_plugin_event(PLUGIN_ID, event, payload)
    except Exception:
        pass


class Service:
    def __init__(self, path=None, ctx=None, hermes=None):
        self.db = Database(path or db_path())
        self.settings = Settings(self.db)
        self.ledger = Ledger(self.db)
        self.graph = Graph(self.db)
        self.registry = Registry(self.db, self.ledger)
        self.prompts = PromptRegistry(self.db)
        self.urls = UrlStore(self.db)
        self.mirror = MirrorStore(self.db, state_dir())
        self.iocs = IocStore(self.db, self.settings)
        self.hermes = hermes or HermesRuntime(ctx)
        self.dataset_lock = threading.Lock()
        self.dataset_state_lock = threading.Lock()
        self.dataset_generation = 0
        self.parts = Parts(self.settings, self.ledger, self.graph, self.iocs,
                           self.hermes, registry=self.registry,
                           prompts=self.prompts, urls=self.urls)
        self.parts.mirror = self.mirror
        self.hunts = HuntService(self.db, self.parts, notify=_broadcast)
        self.parts.spawner = self.hunts
        self.narrator = Narrator(self)
        if ctx is not None:
            self.narrator.attach(ctx)
        self.iocs.seed()
        self.registry.seed()
        self.imported = []
        self.hunts.recover()

    def attach(self, ctx):
        """Give the service the plugin context once the agent half loads."""
        self.hermes.attach(ctx)
        self.narrator.attach(ctx)

    def discover_dataset(self, path, *, allow_excerpts=False, **options):
        """Discover new raw-data patterns after explicit excerpt authorization."""
        if allow_excerpts is not True:
            raise DatasetError("Authorize redacted excerpts before sending data to the host model.")
        if not isinstance(path, str) or not path.strip():
            raise DatasetError("Select an operator-authorized dataset path.")
        if not self.dataset_lock.acquire(blocking=False):
            raise DatasetError("A dataset discovery run is already active.")
        try:
            with self.dataset_state_lock:
                settings = self.settings.all()
                if settings.get("safety.paused") or not settings.get("hunt.use_model"):
                    raise DatasetError("Model discovery is disabled or hunting is paused.")
                generation = self.dataset_generation
            report = DatasetHunter(self.hermes, settings).run(path, **options)
            with self.dataset_state_lock:
                if generation != self.dataset_generation:
                    raise DatasetError("Discovery cancelled by data reset.")
                for card in report["candidates"]:
                    stored, created = self.ledger.add_morphology_candidate(card)
                    report["imported_records"].append({"id": stored["id"], "created": created})
            return report
        finally:
            self.dataset_lock.release()

    def overview(self):
        return {
            "status": self.hunts.status(),
            "capabilities": self.hermes.capabilities(),
            "settings": self.settings.all(),
            "schema_version": SCHEMA_VERSION,
            "imported": self.imported,
        }

    def reset_all_data(self):
        """Stop running hunts, wipe all data, and restore clean initial state."""
        with self.dataset_state_lock:
            self.dataset_generation += 1
            self.hunts.stop()
            self.hunts.shutdown.set()
            for worker in list(self.hunts._workers.values()):
                if worker.is_alive():
                    worker.join(timeout=5)
            self.hunts._workers.clear()
            self.hunts.shutdown.clear()
            self.mirror.clear()
            self.db.reset()
            self.iocs.seed()
            self.registry.seed()
            self.prompts.seed_defaults()
            self.imported = []
            return {"ok": True, "message": "All data wiped. Started fresh from scratch."}


_service = None
_lock = threading.Lock()


def get_service(ctx=None):
    """Return the process-wide service, creating it on first use."""
    global _service
    with _lock:
        if _service is None:
            _service = Service(ctx=ctx)
        elif ctx is not None:
            _service.attach(ctx)
        return _service
