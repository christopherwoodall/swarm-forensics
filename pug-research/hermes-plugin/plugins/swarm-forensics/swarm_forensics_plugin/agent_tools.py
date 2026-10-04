"""Agent tools: native Hermes toolset for interactive threat hunting.

Registers tools into the Hermes tool registry so an agent in a chat
session can inspect context, search indexes, record evidence, propose
indicators, manage swarm groups, and triage false positives.
"""

import json
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

from .analysis import analyze_corpus
from .safety import (
    CLAIM_LEVELS,
    ENTITY_TYPES,
    LINK_KINDS,
    TERM_CATEGORIES,
    screen_content,
    validate_url,
)
from .service import get_service

TOOLSET_NAME = "swarm-forensics"


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _err(msg: str) -> str:
    return _json({"ok": False, "error": str(msg)})


def _resolve_hunt_id(srv, args: dict) -> Optional[str]:
    """Resolve the active or session-bound hunt ID."""
    hunt_id = args.get("hunt_id")
    if hunt_id:
        h = srv.ledger.hunt(hunt_id)
        if h:
            return h["id"]
    sid = (args.get("session_id") or os.getenv("HERMES_SESSION_ID")
           or os.getenv("HERMES_SESSION_KEY"))
    if sid:
        h = srv.ledger.hunt_for_session(sid)
        if h:
            return h["id"]
    h = srv.ledger.active_hunt()
    if h:
        return h["id"]
    latest = next(iter(srv.ledger.hunts(1)), None)
    return latest["id"] if latest else None


# ---------------------------------------------------------------------------
# Tool Handlers
# ---------------------------------------------------------------------------

def sf_get_context(args: dict, service=None, **_: Any) -> str:
    """Return active hunt context: goal, active IOCs, leads, and sources."""
    try:
        srv = service or get_service()
        include_iocs = args.get("include_iocs", True)
        include_leads = args.get("include_leads", True)
        include_sources = args.get("include_sources", True)

        out: Dict[str, Any] = {
            "ok": True,
            "status": srv.hunts.status(),
            "entity_counts": {t: len(srv.graph.list(kind=t)) for t in ENTITY_TYPES},
        }
        if include_iocs:
            out["active_iocs"] = srv.iocs.active_terms()[:50]
            out["ioc_counts"] = srv.iocs.counts()
        if include_leads:
            out["open_leads"] = srv.ledger.open_leads("query", limit=20)
        if include_sources:
            out["enabled_sources"] = srv.registry.sources(enabled_only=True)
        return _json(out)
    except Exception as exc:
        return _err(exc)


def sf_search_index(args: dict, service=None, **_: Any) -> str:
    """Query a public web index adapter (e.g. cdx, wayback, arquivo)."""
    try:
        srv = service or get_service()
        source = str(args.get("source") or "cdx").strip().lower()
        query = str(args.get("query") or "").strip()
        if not query:
            return _err("query must not be empty")

        from .sources import IndexSources, curl_get
        getter = (
            srv.parts.getter
            if hasattr(srv, "parts") and hasattr(srv.parts, "getter")
            else curl_get
        )
        allowed_hosts = srv.registry.allowed_hosts()
        index = IndexSources(
            srv.settings.get("hunt.user_agent", "HermesSwarmForensics/1.0"),
            srv.settings.get("hunt.request_delay_seconds", 0.5),
            srv.settings.get("hunt.index_limit", 50),
            wait=lambda sec: False,
            getter=getter,
            allowed_hosts=allowed_hosts,
        )

        source_cfg = None
        for s in srv.registry.sources():
            if s["name"].lower() == source or s["kind"] == source:
                source_cfg = s
                break
        if not source_cfg:
            source_cfg = source

        queries = index.queries_for(source_cfg, [query])
        if not queries:
            return _json({
                "ok": True,
                "source": source,
                "query": query,
                "outcome": "ok",
                "status": 200,
                "hit_count": 0,
                "hits": [],
            })
        outcome, status, hits = index.run(source_cfg, queries[0])
        return _json({
            "ok": True,
            "source": source,
            "query": query,
            "outcome": outcome,
            "status": status,
            "hit_count": len(hits),
            "hits": hits[:50],
        })
    except Exception as exc:
        return _err(exc)


def sf_record_evidence(args: dict, service=None, **_: Any) -> str:
    """Record verified evidence into the hunt ledger and URL catalog."""
    try:
        srv = service or get_service()
        url = str(args.get("url") or "").strip()
        query = str(args.get("query") or "").strip()
        source = str(args.get("source") or "web").strip()
        title = str(args.get("title") or "").strip()
        excerpt = str(args.get("excerpt") or "").strip()
        claim_level = str(args.get("claim_level") or "L1").strip()

        if not url:
            return _err("url must not be empty")
        if not excerpt:
            return _err("excerpt must not be empty")
        if claim_level not in CLAIM_LEVELS:
            claim_level = "L1"

        screen = screen_content(excerpt)
        tainted = bool(args.get("tainted")) or bool(screen.get("tainted"))

        hunt_id = _resolve_hunt_id(srv, args)
        srv.urls.add(url, source=source)
        eid, created = srv.ledger.add_evidence(
            hunt_id, source, query, url, title, excerpt,
            claim_level=claim_level, tainted=tainted,
        )
        if hunt_id:
            srv.ledger.event(
                hunt_id, "evidence",
                "Recorded %s evidence for %s" % (claim_level, url),
            )
        return _json({
            "ok": True,
            "evidence_id": eid,
            "hunt_id": hunt_id,
            "created": created,
            "url": url,
            "claim_level": claim_level,
            "tainted": tainted,
        })
    except Exception as exc:
        return _err(exc)


def sf_mirror_url(args: dict, service=None, **_: Any) -> str:
    """Capture and safely mirror untrusted web text into local storage."""
    try:
        srv = service or get_service()
        url = str(args.get("url") or "").strip()
        content = args.get("content")
        if not url:
            return _err("url must not be empty")
        if srv.urls.is_benign(url):
            return _err("URL is marked benign and cannot be probed or mirrored")
        clean_url = validate_url(url)
        hunt_id = _resolve_hunt_id(srv, args)
        sid = (args.get("session_id") or os.getenv("HERMES_SESSION_ID")
               or os.getenv("HERMES_SESSION_KEY"))

        if content is None:
            extracted = srv.hermes.web_extract([clean_url])
            if extracted and isinstance(extracted, list) and extracted[0].get("content"):
                content = extracted[0]["content"]
            else:
                return _err("No content provided and web_extract returned no text")

        cfg = srv.settings.all()
        if not cfg.get("mirror.enabled", True):
            return _err("local mirror is disabled in settings")
        max_bytes = int(cfg.get("mirror.max_bytes", 500_000))
        result = srv.mirror.save_extract(
            clean_url, str(content), hunt_id=hunt_id, session_id=sid,
            max_bytes=max_bytes,
        )
        if not result:
            return _err("failed to write mirror file")
        srv.urls.add(clean_url, source="mirror")
        if hunt_id:
            summary = "mirrored %d bytes (sha256: %s)" % (
                result["byte_count"], result["sha256"][:12])
            srv.ledger.record_corpus_observation(
                hunt_id=hunt_id, session_id=sid, tool_name="sf_mirror_url",
                query_or_url=clean_url, status="mirrored",
                result_summary=summary, sha256=result["sha256"],
            )
        return _json({
            "ok": True,
            "mirror": result,
        })
    except Exception as exc:
        return _err(exc)


def sf_analyze_corpus(args: dict, service=None, **_: Any) -> str:
    """Execute deterministic TTP analysis on observed corpus traces."""
    try:
        srv = service or get_service()
        query = args.get("query")
        hunt_id = _resolve_hunt_id(srv, args)
        observations = srv.ledger.corpus_observations(hunt_id=hunt_id, limit=200)
        evidence = srv.ledger.list_evidence(hunt_id=hunt_id, limit=200)
        urls = srv.urls.list(limit=200)
        analysis_result = analyze_corpus(observations, evidence, urls, query=query)
        return _json(analysis_result)
    except Exception as exc:
        return _err(exc)


def sf_propose_ioc(args: dict, service=None, **_: Any) -> str:
    """Propose an Indicator of Compromise (IOC) for review."""
    try:
        srv = service or get_service()
        term = str(args.get("term") or "").strip()
        category = str(args.get("category") or "proposed").strip().lower()
        reason = str(args.get("reason") or "proposed via interactive session").strip()
        evidence_id = args.get("evidence_id")

        if not term:
            return _err("term must not be empty")
        if category not in TERM_CATEGORIES:
            category = "proposed"

        ioc, outcome = srv.iocs.propose(
            term, category=category, provenance=reason,
            evidence_id=evidence_id, actor="model", note=reason,
        )
        if not ioc:
            return _json({"ok": False, "reason": outcome, "term": term})
        return _json({
            "ok": True,
            "ioc": ioc,
            "reason": outcome,
        })
    except Exception as exc:
        return _err(exc)


def sf_manage_entity(args: dict, service=None, **_: Any) -> str:
    """Create, update, or tag an entity (artifact, agent, swarm, campaign, collection)."""
    try:
        srv = service or get_service()
        action = str(args.get("action") or "upsert").strip().lower()
        entity_type = str(args.get("type") or "agent").strip().lower()
        name = str(args.get("name") or "").strip()
        summary = str(args.get("summary") or "").strip()
        tags = args.get("tags") or []
        notes = args.get("notes")

        if not name:
            return _err("name must not be empty")

        if action == "upsert":
            ent = srv.graph.upsert(
                entity_type, name, summary=summary,
                origin="model", tags=tags,
            )
            if notes:
                ent = srv.graph.update(ent["id"], notes=notes)
            return _json({"ok": True, "entity": ent})
        elif action in ("get", "tag"):
            ent = srv.graph.find(entity_type, name) if entity_type else None
            if not ent:
                for candidate_type in ENTITY_TYPES:
                    ent = srv.graph.find(candidate_type, name)
                    if ent:
                        break
            if not ent:
                return _err("entity not found")
            if action == "tag":
                existing_tags = set(ent.get("tags") or [])
                existing_tags.update(str(t).strip() for t in tags if str(t).strip())
                ent = srv.graph.update(ent["id"], tags=list(existing_tags))
            return _json({"ok": True, "entity": ent})
        else:
            return _err("unsupported action: %s" % action)
    except Exception as exc:
        return _err(exc)


def sf_link_entities(args: dict, service=None, **_: Any) -> str:
    """Connect two entities via hierarchical or loose relationship."""
    try:
        srv = service or get_service()
        src_name = str(args.get("src_name") or "").strip()
        src_type = str(args.get("src_type") or "").strip()
        dst_name = str(args.get("dst_name") or "").strip()
        dst_type = str(args.get("dst_type") or "").strip()
        kind = str(args.get("kind") or "part_of").strip().lower()

        if not src_name or not dst_name:
            return _err("src_name and dst_name are required")
        if kind not in LINK_KINDS and kind != "mentions":
            return _err("kind must be one of: %s" % ", ".join(LINK_KINDS))

        src_ent = srv.graph.find(src_type, src_name) if src_type else None
        if not src_ent:
            for t in ENTITY_TYPES:
                src_ent = srv.graph.find(t, src_name)
                if src_ent:
                    break
        if not src_ent:
            return _err("source entity '%s' not found" % src_name)

        dst_ent = srv.graph.find(dst_type, dst_name) if dst_type else None
        if not dst_ent:
            for t in ENTITY_TYPES:
                dst_ent = srv.graph.find(t, dst_name)
                if dst_ent:
                    break
        if not dst_ent:
            return _err("target entity '%s' not found" % dst_name)

        link_id = srv.graph.link(src_ent["id"], dst_ent["id"], kind)
        return _json({
            "ok": True,
            "link_id": link_id,
            "src": src_ent["name"],
            "dst": dst_ent["name"],
            "kind": kind,
        })
    except Exception as exc:
        return _err(exc)


def sf_triage_item(args: dict, service=None, **_: Any) -> str:
    """Triage an indicator, URL, or lead (e.g. mark benign, dismiss, or active)."""
    try:
        srv = service or get_service()
        item_type = str(args.get("item_type") or "").strip().lower()
        target = str(args.get("target") or "").strip()
        verdict = str(args.get("verdict") or "benign").strip().lower()
        reason = str(args.get("reason") or "triaged by analyst").strip()

        if not target:
            return _err("target must not be empty")

        if item_type == "url":
            triaged = srv.urls.triage(target, verdict, reason=reason)
            return _json({"ok": True, "item_type": "url", "item": triaged})
        elif item_type == "ioc":
            ioc_row = None
            if target.isdigit():
                ioc_row = srv.iocs.detail(int(target))
            if not ioc_row:
                for row in srv.iocs.list(query=target, limit=10):
                    if row["term"].lower() == target.lower():
                        ioc_row = row
                        break
            if not ioc_row:
                return _err("ioc '%s' not found" % target)
            updated = srv.iocs.decide(ioc_row["id"], verdict, reason=reason)
            return _json({"ok": True, "item_type": "ioc", "item": updated})
        elif item_type == "lead":
            lead_id = int(target) if target.isdigit() else 0
            lead_status = verdict if verdict in ("done", "dismissed") else "dismissed"
            closed = srv.ledger.close_lead(lead_id, status=lead_status)
            return _json({"ok": True, "item_type": "lead", "closed": closed})
        else:
            return _err("item_type must be 'url', 'ioc', or 'lead'")
    except Exception as exc:
        return _err(exc)


def sf_query_knowledge(args: dict, service=None, **_: Any) -> str:
    """Search across entities, IOCs, URLs, leads, and evidence."""
    try:
        srv = service or get_service()
        query = str(args.get("query") or "").strip()
        kind = str(args.get("kind") or "all").strip().lower()

        results: Dict[str, Any] = {"ok": True, "query": query}
        if kind in ("all", "entities"):
            results["entities"] = srv.graph.list(query=query, limit=20)
        if kind in ("all", "iocs"):
            results["iocs"] = srv.iocs.list(query=query, limit=20)
        if kind in ("all", "urls"):
            results["urls"] = srv.urls.list(query=query, limit=20)
        if kind in ("all", "leads"):
            results["leads"] = [lead for lead in srv.ledger.open_leads("query", limit=20)
                                if query.lower() in lead["value"].lower()]
        return _json(results)
    except Exception as exc:
        return _err(exc)


def sf_spawn_subhunt(args: dict, service=None, **_: Any) -> str:
    """Spawn a recursive child hunt up to the maximum configured depth."""
    try:
        srv = service or get_service()
        goal = str(args.get("goal") or "").strip()
        parent_hunt_id = args.get("parent_hunt_id")
        max_cycles = int(args.get("max_cycles", 0))
        if not parent_hunt_id:
            active = srv.ledger.active_hunt()
            if not active:
                return _err("No active hunt to spawn from. Provide parent_hunt_id.")
            parent_hunt_id = active["id"]
        child = srv.hunts.spawn_subhunt(parent_hunt_id, goal=goal, max_cycles=max_cycles)
        return _json({
            "ok": True,
            "hunt_id": child["id"],
            "parent_hunt_id": child["parent_hunt_id"],
            "depth": child["depth"],
            "goal": child["goal"],
            "state": child["state"],
            "message": "Spawned child hunt %s at depth %d" % (child["id"], child["depth"]),
        })
    except Exception as exc:
        return _err(exc)


def sf_attach_hunt(args: dict, service=None, **_: Any) -> str:
    """Inspect and attach to an existing hunt or session."""
    try:
        srv = service or get_service()
        target = str(args.get("hunt_id") or args.get("target") or "").strip()
        hunt = None
        if target:
            hunt = srv.ledger.hunt(target) or srv.ledger.hunt_by_session(target)
        else:
            hunt = srv.ledger.active_hunt()
        if not hunt:
            return _err("Hunt not found for %s" % (target or "active"))
        calling_sid = (args.get("session_id") or os.getenv("HERMES_SESSION_ID")
                       or os.getenv("HERMES_SESSION_KEY"))
        calling_skey = os.getenv("HERMES_SESSION_KEY") or ""
        if calling_sid:
            srv.ledger.bind_session(hunt["id"], calling_sid, calling_skey)
        children = srv.ledger.child_hunts(hunt["id"])
        events = srv.ledger.events(hunt["id"], 0, limit=5)
        return _json({
            "ok": True,
            "hunt": hunt,
            "children": children,
            "recent_events": events,
            "bound_session": calling_sid or hunt.get("session_id"),
            "message": "Attached to hunt %s (depth %d, cycle %d)" % (
                hunt["id"], hunt.get("depth", 0), hunt["cycle"]),
        })
    except Exception as exc:
        return _err(exc)


# ---------------------------------------------------------------------------
# Tool Declarations & Manifest
# ---------------------------------------------------------------------------

AGENT_TOOLS: List[Tuple[str, Callable, str, dict, list]] = [
    (
        "sf_get_context",
        sf_get_context,
        "Inspect active hunt context: goal, indicators, open leads, and allowlist.",
        {
            "include_iocs": {
                "type": "boolean",
                "description": "Include active IOC terms (default: true).",
            },
            "include_leads": {
                "type": "boolean",
                "description": "Include open research leads (default: true).",
            },
            "include_sources": {
                "type": "boolean",
                "description": "Include enabled public indexes (default: true).",
            },
        },
        [],
    ),
    (
        "sf_search_index",
        sf_search_index,
        "Query a public web index adapter (e.g. cdx, wayback, arquivo) for observations.",
        {
            "source": {
                "type": "string",
                "description": "Target index (e.g. 'cdx', 'wayback', 'arquivo'). Default: cdx.",
            },
            "query": {
                "type": "string",
                "description": "Target domain, path, or URL wildcard pattern.",
            },
        },
        ["query"],
    ),
    (
        "sf_record_evidence",
        sf_record_evidence,
        "Record verified evidence into the hunt ledger with provenance and claim level.",
        {
            "url": {
                "type": "string",
                "description": "Source URL where evidence was observed.",
            },
            "query": {
                "type": "string",
                "description": "Search query or pattern that retrieved the page.",
            },
            "source": {
                "type": "string",
                "description": "Origin of evidence (e.g. 'web', 'cdx', 'archive').",
            },
            "excerpt": {
                "type": "string",
                "description": "Exact text excerpt containing agent traces.",
            },
            "title": {
                "type": "string",
                "description": "Optional page title.",
            },
            "claim_level": {
                "type": "string",
                "enum": ["L1", "L2", "L3", "L4", "L5"],
                "description": "Claim ladder level.",
            },
            "tainted": {
                "type": "boolean",
                "description": "Set to true if page contained prompt injection attempts.",
            },
        },
        ["url", "excerpt"],
    ),
    (
        "sf_mirror_url",
        sf_mirror_url,
        "Safely capture and locally mirror untrusted web text from an investigation artifact.",
        {
            "url": {
                "type": "string",
                "description": "Public HTTP or HTTPS URL to mirror.",
            },
            "content": {
                "type": "string",
                "description": "Optional page content if already fetched.",
            },
            "hunt_id": {
                "type": "string",
                "description": "Optional hunt ID to associate with the mirror artifact.",
            },
        },
        ["url"],
    ),
    (
        "sf_analyze_corpus",
        sf_analyze_corpus,
        "Run deterministic TTP analysis across observed corpus traces, relays, and nonces.",
        {
            "query": {
                "type": "string",
                "description": "Optional query or candidate URL to test against corpus.",
            },
            "hunt_id": {
                "type": "string",
                "description": "Optional hunt ID to scope analysis to.",
            },
        },
        [],
    ),
    (
        "sf_propose_ioc",
        sf_propose_ioc,
        "Submit an indicator of compromise (IOC) to the review catalog with category.",
        {
            "term": {
                "type": "string",
                "description": "Specific indicator string (host, parameter shape, nonce).",
            },
            "category": {
                "type": "string",
                "enum": list(TERM_CATEGORIES),
                "description": "Indicator category.",
            },
            "reason": {
                "type": "string",
                "description": "Rationale and provenance explaining why this is an IOC.",
            },
            "evidence_id": {
                "type": "integer",
                "description": "Optional evidence ID supporting this indicator.",
            },
        },
        ["term"],
    ),
    (
        "sf_manage_entity",
        sf_manage_entity,
        "Create, update, or tag an entity (artifact, agent, swarm, campaign, collection).",
        {
            "action": {
                "type": "string",
                "enum": ["upsert", "get", "tag"],
                "description": "Entity action.",
            },
            "type": {
                "type": "string",
                "enum": list(ENTITY_TYPES),
                "description": "Entity classification.",
            },
            "name": {
                "type": "string",
                "description": "Unique entity name.",
            },
            "summary": {
                "type": "string",
                "description": "Brief description of the entity.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tags or labels.",
            },
            "notes": {
                "type": "string",
                "description": "Optional Markdown notes for the entity.",
            },
        },
        ["name", "type"],
    ),
    (
        "sf_link_entities",
        sf_link_entities,
        "Connect two entities via hierarchical or loose relationships.",
        {
            "src_name": {
                "type": "string",
                "description": "Source entity name.",
            },
            "dst_name": {
                "type": "string",
                "description": "Target entity name.",
            },
            "src_type": {
                "type": "string",
                "description": "Optional source entity type.",
            },
            "dst_type": {
                "type": "string",
                "description": "Optional target entity type.",
            },
            "kind": {
                "type": "string",
                "enum": list(LINK_KINDS),
                "description": "Relationship kind.",
            },
        },
        ["src_name", "dst_name", "kind"],
    ),
    (
        "sf_triage_item",
        sf_triage_item,
        "Triage an indicator, URL, or lead (mark benign, dismiss, or active).",
        {
            "item_type": {
                "type": "string",
                "enum": ["url", "ioc", "lead"],
                "description": "Type of item to triage.",
            },
            "target": {
                "type": "string",
                "description": "URL string, IOC term, or lead ID to triage.",
            },
            "verdict": {
                "type": "string",
                "description": "Triage status: 'benign', 'active', 'rejected', 'dismissed'.",
            },
            "reason": {
                "type": "string",
                "description": "Analyst explanation for the triage verdict.",
            },
        },
        ["item_type", "target", "verdict"],
    ),
    (
        "sf_query_knowledge",
        sf_query_knowledge,
        "Search across entities, indicators, URLs, leads, and evidence in the database.",
        {
            "query": {
                "type": "string",
                "description": "Search term or pattern.",
            },
            "kind": {
                "type": "string",
                "enum": ["all", "entities", "iocs", "urls", "leads"],
                "description": "Scope of search.",
            },
        },
        ["query"],
    ),
    (
        "sf_spawn_subhunt",
        sf_spawn_subhunt,
        "Spawn a recursive child hunt crawler up to the maximum configured depth (default 3).",
        {
            "goal": {
                "type": "string",
                "description": "Specific investigation goal for the child crawler.",
            },
            "parent_hunt_id": {
                "type": "string",
                "description": "Optional parent hunt ID. Defaults to the currently active hunt.",
            },
            "max_cycles": {
                "type": "integer",
                "description": "Optional max cycles for the child hunt.",
            },
        },
        ["goal"],
    ),
    (
        "sf_attach_hunt",
        sf_attach_hunt,
        "Inspect details and attachment state of a running or historical hunt by ID or session ID.",
        {
            "hunt_id": {
                "type": "string",
                "description": "The hunt ID or session ID to attach to or inspect.",
            },
        },
        [],
    ),
]


def register_tools(ctx) -> None:
    """Register all Swarm Forensics tools with the Hermes host context."""
    if not hasattr(ctx, "register_tool"):
        return
    for name, handler, description, properties, required in AGENT_TOOLS:
        parameters: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            parameters["required"] = required
        schema = {
            "name": name,
            "description": description,
            "parameters": parameters,
        }
        ctx.register_tool(
            name=name,
            toolset=TOOLSET_NAME,
            schema=schema,
            handler=handler,
            description=description,
            emoji="🔍",
        )
