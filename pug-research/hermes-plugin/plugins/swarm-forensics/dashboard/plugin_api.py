"""Swarm Forensics backend routes, mounted at /api/plugins/swarm-forensics.

Hermes imports this file on its own, so it adds the plugin directory to
sys.path and imports the shared engine. Every route is a thin wrapper
over the service. Domain errors map to 4xx. Handlers are sync functions,
so FastAPI runs them in its thread pool and database calls never block
the event loop.
"""

import sys
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException, Query

_PLUGIN_DIR = Path(__file__).resolve().parents[1]
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))

from swarm_forensics_plugin.entities import EntityError  # noqa: E402
from swarm_forensics_plugin.extract import extract_indicators  # noqa: E402
from swarm_forensics_plugin.hunt import HuntRefused  # noqa: E402
from swarm_forensics_plugin.iocs import IocError  # noqa: E402
from swarm_forensics_plugin.schedule import ScheduleError  # noqa: E402
from swarm_forensics_plugin.service import get_service  # noqa: E402
from swarm_forensics_plugin.settings import Settings, SettingsError  # noqa: E402

router = APIRouter()
_started = False


def _svc():
    global _started
    service = get_service()
    if not _started:
        service.hunts.ensure_scheduler()
        _started = True
    return service


def _run(fn, *args, **kwargs):
    """Call fn and translate domain errors into HTTP errors."""
    try:
        return fn(*args, **kwargs)
    except SettingsError as exc:
        raise HTTPException(422, {"errors": exc.errors})
    except (HuntRefused,) as exc:
        raise HTTPException(409, str(exc))
    except (IocError, EntityError, ScheduleError, ValueError) as exc:
        raise HTTPException(400, str(exc))


def _found(value):
    if value is None:
        raise HTTPException(404, "not found")
    return value


# -- status and hunts ---------------------------------------------------------

@router.get("/overview")
def overview():
    return _svc().overview()


@router.post("/heartbeat")
def heartbeat():
    return _svc().hunts.heartbeat()


@router.get("/status")
def status():
    return _svc().hunts.status()


@router.post("/hunts/start")
def hunt_start(body: dict = Body(default_factory=dict)):
    return _run(_svc().hunts.start, "desktop", body.get("goal"),
                int(body.get("max_cycles") or 0))


@router.post("/hunts/stop")
def hunt_stop(body: dict = Body(default_factory=dict)):
    return _run(_svc().hunts.stop, body.get("hunt_id"))


@router.post("/hunts/pause")
def hunt_pause(body: dict = Body(default_factory=dict)):
    return _run(_svc().hunts.pause, body.get("hunt_id"))


@router.post("/hunts/resume")
def hunt_resume(body: dict = Body(default_factory=dict)):
    return _run(_svc().hunts.resume, body.get("hunt_id"))


@router.get("/hunts")
def hunts(limit: int = 50):
    return {"hunts": _svc().ledger.hunts(limit)}


@router.get("/hunts/{hunt_id}")
def hunt(hunt_id: str):
    return _found(_svc().ledger.hunt(hunt_id))


@router.get("/events")
def events(hunt_id: str = None, after: int = 0, limit: int = 200):
    return {"events": _svc().ledger.events(hunt_id, after, limit)}


@router.get("/leads")
def leads(limit: int = 50):
    return {"leads": _svc().ledger.open_leads(limit=limit)}


@router.post("/leads")
def add_lead(body: dict = Body(...)):
    kind, value = body.get("kind"), str(body.get("value") or "").strip()
    if kind not in ("query", "url") or not value:
        raise HTTPException(400, "kind must be query or url, with a value")
    return {"added": _svc().ledger.add_lead(kind, value, 0.9, "human")}


# -- evidence and IOCs --------------------------------------------------------

@router.get("/evidence")
def evidence(q: str = None, min_level: str = None, hunt_id: str = None,
             limit: int = 100, offset: int = 0):
    return {"evidence": _svc().ledger.list_evidence(
        q, min_level, hunt_id, limit, offset)}


@router.get("/evidence/{evidence_id}")
def evidence_one(evidence_id: int):
    return _found(_svc().ledger.evidence(evidence_id))


@router.get("/iocs")
def iocs(status: str = None, q: str = None, limit: int = 500, offset: int = 0):
    service = _svc()
    return {"iocs": _run(service.iocs.list, status, q, limit, offset),
            "counts": service.iocs.counts()}


@router.get("/iocs/{ioc_id}")
def ioc_one(ioc_id: int):
    return _found(_svc().iocs.detail(ioc_id))


@router.post("/iocs")
def ioc_add(body: dict = Body(...)):
    service = _svc()
    ioc, reason = service.iocs.propose(
        body.get("term"), body.get("category") or "proposed",
        provenance="operator", note=str(body.get("note") or ""), actor="human")
    if ioc is None:
        raise HTTPException(400, "term refused: %s" % reason)
    if body.get("activate") and ioc["status"] == "proposed":
        ioc = _run(service.iocs.decide, ioc["id"], "accept", "added by operator")
    return ioc


@router.post("/iocs/{ioc_id}/decision")
def ioc_decide(ioc_id: int, body: dict = Body(...)):
    return _run(_svc().iocs.decide, ioc_id, body.get("decision"),
                str(body.get("reason") or ""), body.get("narrower"))


# -- entity graph -------------------------------------------------------------

@router.get("/entities")
def entities(type: str = None, q: str = None, limit: int = 200):
    return {"entities": _run(_svc().graph.list, type, q, limit)}


@router.post("/entities")
def entity_add(body: dict = Body(...)):
    service = _svc()
    entity = _run(service.graph.upsert, body.get("type"), body.get("name"),
                  str(body.get("summary") or ""), body.get("attrs"), "human")
    if body.get("notes"):
        entity = _run(service.graph.update, entity["id"],
                      notes=str(body["notes"]))
    return entity


@router.get("/entities/{entity_id}")
def entity_one(entity_id: str):
    return _found(_svc().graph.view(entity_id))


@router.put("/entities/{entity_id}")
def entity_update(entity_id: str, body: dict = Body(...)):
    return _run(_svc().graph.update, entity_id, body.get("name"),
                body.get("summary"), body.get("notes"), body.get("attrs"))


@router.delete("/entities/{entity_id}")
def entity_delete(entity_id: str):
    if not _svc().graph.delete(entity_id):
        raise HTTPException(404, "not found")
    return {"deleted": True}


@router.post("/links")
def link_add(body: dict = Body(...)):
    link_id = _run(_svc().graph.link, body.get("src"), body.get("dst"),
                   body.get("kind"))
    return {"id": link_id}


@router.delete("/links/{link_id}")
def link_delete(link_id: int):
    if not _svc().graph.unlink(link_id):
        raise HTTPException(404, "not found")
    return {"deleted": True}


@router.get("/graph")
def graph(center: str = None, depth: int = 2,
          types: str = Query(default=None, description="comma separated")):
    wanted = [t for t in (types or "").split(",") if t] or None
    return _svc().graph.graph(center, depth, wanted)


@router.post("/extract-preview")
def extract_preview(body: dict = Body(...)):
    pairs = extract_indicators(str(body.get("text") or "")[:100000])
    return {"indicators": [{"kind": k, "value": v} for k, v in pairs]}


# -- settings and schedules ---------------------------------------------------

@router.get("/settings")
def settings_get():
    return {"values": _svc().settings.all(), "schema": Settings.schema()}


@router.put("/settings")
def settings_put(body: dict = Body(...)):
    return {"values": _run(_svc().settings.update, body.get("updates") or {})}


@router.get("/schedules")
def schedules_get():
    return {"schedules": _svc().hunts.schedules()}


@router.post("/schedules")
def schedule_add(body: dict = Body(...)):
    sid = _run(_svc().hunts.add_schedule, body.get("name"), body.get("kind"),
               str(body.get("spec") or ""), body.get("goal"),
               int(body.get("max_cycles") or 5))
    return {"id": sid}


@router.post("/schedules/{schedule_id}/arm")
def schedule_arm(schedule_id: str, body: dict = Body(...)):
    _run(_svc().hunts.arm_schedule, schedule_id, bool(body.get("armed")))
    return {"schedules": _svc().hunts.schedules()}


@router.delete("/schedules/{schedule_id}")
def schedule_delete(schedule_id: str):
    if not _svc().hunts.delete_schedule(schedule_id):
        raise HTTPException(404, "not found")
    return {"deleted": True}
