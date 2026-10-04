"""Service: wires storage, policy, research, and lifecycle together.

One service per process. The desktop API, the `/swarm-forensics` command,
and the scheduler all call the same object, so they see the same state.
"""

import threading

from .db import Database
from .entities import Graph
from .hermes import HermesRuntime
from .hunt import HuntService
from .iocs import IocStore
from .ledger import Ledger
from .legacy import find_state_dirs, import_state
from .paths import PLUGIN_ID, db_path
from .research import Parts
from .settings import SCHEMA_VERSION, Settings


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
        self.iocs = IocStore(self.db, self.settings)
        self.hermes = hermes or HermesRuntime(ctx)
        parts = Parts(self.settings, self.ledger, self.graph, self.iocs,
                      self.hermes)
        self.hunts = HuntService(self.db, parts, notify=_broadcast)
        self.iocs.seed()
        self.imported = [dict(import_state(self.db, d), path=str(d))
                         for d in find_state_dirs()]
        self.hunts.recover()

    def attach(self, ctx):
        """Give the service the plugin context once the agent half loads."""
        self.hermes.attach(ctx)

    def overview(self):
        return {
            "status": self.hunts.status(),
            "capabilities": self.hermes.capabilities(),
            "settings": self.settings.all(),
            "schema_version": SCHEMA_VERSION,
            "imported": self.imported,
        }


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
