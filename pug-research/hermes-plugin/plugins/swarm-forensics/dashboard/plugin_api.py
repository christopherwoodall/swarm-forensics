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
from swarm_forensics_plugin.export import export_all  # noqa: E402
from swarm_forensics_plugin.extract import extract_indicators  # noqa: E402
from swarm_forensics_plugin.hunt import HuntRefused  # noqa: E402
from swarm_forensics_plugin.iocs import IocError  # noqa: E402
from swarm_forensics_plugin.prompt_registry import PromptError  # noqa: E402
from swarm_forensics_plugin.registry import RegistryError  # noqa: E402
from swarm_forensics_plugin.schedule import ScheduleError  # noqa: E402
from swarm_forensics_plugin.service import get_service  # noqa: E402
from swarm_forensics_plugin.settings import Settings, SettingsError  # noqa: E402
from swarm_forensics_plugin.url_store import UrlError  # noqa: E402

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
    except (IocError, EntityError, ScheduleError, ValueError, RegistryError,
            PromptError, UrlError) as exc:
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


@router.post("/hunts/{hunt_id}/spawn")
def hunt_spawn(hunt_id: str, body: dict = Body(default_factory=dict)):
    return _run(_svc().hunts.spawn_subhunt, hunt_id, body.get("goal"),
                int(body.get("max_cycles") or 0))


@router.get("/hunts/{hunt_id}/children")
def hunt_children(hunt_id: str):
    return {"children": _svc().ledger.child_hunts(hunt_id)}


@router.get("/events")
def events(hunt_id: str = None, after: int = 0, limit: int = 200,
           kind: str = None, level: str = None):
    return {"events": _svc().ledger.events(hunt_id, after, limit, kind=kind, level=level)}


@router.get("/leads")
def leads(limit: int = 50):
    return {"leads": _svc().ledger.open_leads(limit=limit)}


@router.post("/leads")
def add_lead(body: dict = Body(...)):
    kind, value = body.get("kind"), str(body.get("value") or "").strip()
    if kind not in ("query", "url") or not value:
        raise HTTPException(400, "kind must be query or url, with a value")
    return {"added": _svc().ledger.add_lead(kind, value, 0.9, "human")}


@router.post("/leads/{lead_id}/close")
def lead_close(lead_id: int, body: dict = Body(default_factory=dict)):
    status = body.get("status") or "done"
    if not _run(_svc().ledger.close_lead, lead_id, status=status):
        raise HTTPException(404, "not found")
    return {"closed": True}


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


@router.post("/iocs/import")
def iocs_import(body: dict = Body(...)):
    service = _svc()
    return _run(service.registry.import_wordlist,
                str(body.get("text") or ""), service.iocs,
                activate=bool(body.get("activate")))


# -- entity graph -------------------------------------------------------------

@router.get("/entities")
def entities(type: str = None, q: str = None, limit: int = 200):
    return {"entities": _run(_svc().graph.list, type, q, limit)}


@router.post("/entities")
def entity_add(body: dict = Body(...)):
    service = _svc()
    entity = _run(service.graph.upsert, body.get("type"), body.get("name"),
                  str(body.get("summary") or ""), body.get("attrs"), "human",
                  tags=body.get("tags"))
    if body.get("notes"):
        entity = _run(service.graph.update, entity["id"],
                      notes=str(body["notes"]))
    return entity


@router.post("/entities/group")
def group_create(body: dict = Body(...)):
    service = _svc()
    gtype = body.get("type") or "swarm"
    name = body.get("name")
    summary = str(body.get("summary") or "")
    tags = body.get("tags") or []
    members = body.get("members") or []
    entity = _run(service.graph.upsert, gtype, name, summary=summary,
                  origin="human", tags=tags)
    linked = 0
    for member_name in members:
        member_ent = None
        for t in ("agent", "artifact", "swarm", "collection"):
            member_ent = service.graph.find(t, member_name)
            if member_ent:
                break
        if member_ent:
            service.graph.link(member_ent["id"], entity["id"], "part_of")
            linked += 1
    return {"entity": entity, "members_linked": linked}


@router.get("/entities/{entity_id}")
def entity_one(entity_id: str):
    return _found(_svc().graph.view(entity_id))


@router.put("/entities/{entity_id}")
def entity_update(entity_id: str, body: dict = Body(...)):
    return _run(_svc().graph.update, entity_id, body.get("name"),
                body.get("summary"), body.get("notes"), body.get("attrs"),
                tags=body.get("tags"))


@router.post("/entities/{entity_id}/tag")
def entity_tag(entity_id: str, body: dict = Body(...)):
    service = _svc()
    tags = body.get("tags") or []
    ent = _found(service.graph.get(entity_id))
    existing = set(ent.get("tags") or [])
    existing.update(str(t).strip() for t in tags if str(t).strip())
    return _run(service.graph.update, entity_id, tags=list(existing))


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


# -- sources and grammar ------------------------------------------------------

@router.get("/sources")
def sources():
    return {"sources": _svc().registry.sources()}


@router.post("/sources")
def source_add(body: dict = Body(...)):
    return _run(_svc().registry.add_source,
                body.get("name"), body.get("kind"), body.get("endpoint"),
                config=body.get("config"), note=str(body.get("note") or ""))


@router.put("/sources/{source_id}")
def source_update(source_id: int, body: dict = Body(...)):
    fields = {k: v for k, v in body.items() if k in (
        "enabled", "endpoint", "config", "note", "probe_candidates")}
    return _run(_svc().registry.update_source, source_id, **fields)


@router.delete("/sources/{source_id}")
def source_delete(source_id: int):
    if not _svc().registry.delete_source(source_id):
        raise HTTPException(404, "not found")
    return {"deleted": True}


@router.get("/grammar")
def grammar_get(kind: str = None):
    return {"grammar": _svc().registry.grammar(kind=kind)}


@router.post("/grammar")
def grammar_add(body: dict = Body(...)):
    return _run(_svc().registry.add_grammar,
                body.get("kind"), body.get("value"),
                param=str(body.get("param") or ""),
                note=str(body.get("note") or ""))


@router.put("/grammar/{grammar_id}")
def grammar_update(grammar_id: int, body: dict = Body(...)):
    return _run(_svc().registry.set_grammar_enabled,
                grammar_id, bool(body.get("enabled")))


@router.delete("/grammar/{grammar_id}")
def grammar_delete(grammar_id: int):
    if not _svc().registry.delete_grammar(grammar_id):
        raise HTTPException(404, "not found")
    return {"deleted": True}


@router.post("/grammar/regenerate")
def grammar_regenerate():
    service = _svc()
    from swarm_forensics_plugin.predict import generate_candidates
    bundle = service.registry.grammar_bundle()
    pairs = generate_candidates(bundle)
    added = 0
    for url, _template in pairs:
        if service.ledger.add_lead("candidate", url, priority=0.6, origin="grammar"):
            added += 1
    return {"added": added}


# -- prompts ------------------------------------------------------------------

@router.get("/prompts")
def prompts_list():
    return {"prompts": _svc().prompts.list()}


@router.get("/prompts/{prompt_id}")
def prompt_one(prompt_id: str):
    return _found(_svc().prompts.get(prompt_id))


@router.put("/prompts/{prompt_id}")
def prompt_update(prompt_id: str, body: dict = Body(...)):
    template = body.get("template")
    if template is None:
        raise HTTPException(400, "template is required")
    return _run(_svc().prompts.update, prompt_id, str(template))


@router.post("/prompts/{prompt_id}/reset")
def prompt_reset(prompt_id: str):
    return _run(_svc().prompts.reset, prompt_id)


@router.get("/prompts-export")
def prompts_export():
    return {"prompts": _svc().prompts.export_all()}


@router.post("/prompts-import")
def prompts_import(body: dict = Body(...)):
    data = body.get("prompts") if isinstance(body.get("prompts"), dict) else body
    count = _run(_svc().prompts.import_all, data)
    return {"imported": count, "prompts": _svc().prompts.list()}


# -- urls catalog -------------------------------------------------------------

@router.get("/urls")
def urls_list(status: str = None, q: str = None, limit: int = 200, offset: int = 0):
    service = _svc()
    return {
        "urls": _run(service.urls.list, status, q, limit, offset),
        "counts": service.urls.counts(),
    }


@router.post("/urls/triage")
def url_triage(body: dict = Body(...)):
    service = _svc()
    url = body.get("url")
    status = body.get("status") or "benign"
    reason = str(body.get("reason") or "")
    if not url:
        raise HTTPException(400, "url is required")
    return {"item": _run(service.urls.triage, url, status, reason)}


# -- export -------------------------------------------------------------------

@router.post("/export")
def export_data():
    return _run(export_all, _svc())


# -- reset --------------------------------------------------------------------

@router.post("/reset")
def reset_database():
    return _run(_svc().reset_all_data)


# -- session and mirror routes ------------------------------------------------

@router.get("/sessions/{session_id}/overview")
def session_overview(session_id: str):
    svc = _svc()
    hunt = svc.ledger.hunt_for_session(session_id)
    hid = hunt["id"] if hunt else None
    return {
        "session_id": session_id,
        "hunt": hunt,
        "events": svc.ledger.events(hid, 0, 30),
        "corpus": svc.ledger.corpus_observations(hunt_id=hid, session_id=session_id, limit=30),
        "open_leads": svc.ledger.open_leads(limit=10),
        "mirrors_count": svc.mirror.count(),
    }


@router.post("/sessions/{session_id}/bind")
def session_bind(session_id: str, body: dict = Body(default_factory=dict)):
    hunt_id = body.get("hunt_id")
    if not hunt_id:
        active = _svc().ledger.active_hunt()
        if not active:
            raise HTTPException(404, "no active hunt found to bind")
        hunt_id = active["id"]
    _svc().ledger.bind_session(hunt_id, session_id, body.get("session_key", ""))
    return {"ok": True, "session_id": session_id, "hunt_id": hunt_id}


@router.get("/mirrors")
def mirrors_list(limit: int = 50):
    svc = _svc()
    return {
        "mirrors": svc.mirror.list_mirrors(limit=limit),
        "total": svc.mirror.count(),
    }


@router.get("/mirrors/{target}")
def mirror_detail(target: str, include_text: bool = Query(False)):
    svc = _svc()
    meta = svc.mirror.get_mirror(target)
    if not meta:
        raise HTTPException(404, "mirror artifact not found")
    out = dict(meta)
    if include_text:
        out["content"] = svc.mirror.read_text(target)
    return out


@router.get("/corpus")
def corpus_list(hunt_id: str = None, session_id: str = None, limit: int = 50):
    return {
        "observations": _svc().ledger.corpus_observations(
            hunt_id=hunt_id, session_id=session_id, limit=limit,
        ),
    }


