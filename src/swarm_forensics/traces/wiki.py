"""Wiki reservoir normalizer.

Emits one event row per revision (added-text reconstruction) and per
save/delete/revert/probe event. Labels map to actor hints with investigator
labels separated out, and no row asserts an agent identity.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from swarm_forensics.traces.readers import iter_wiki_events, iter_wiki_revisions
from swarm_forensics.traces.rows import (
    actor_hint_for_label,
    added_text,
    hash_prefix,
    mk_event,
    short,
)

UQ_REPORT_PATTERN = __import__("re").compile(r"urlquery\.net/report/([0-9a-f-]{36})")


def _rev_event(rev: dict[str, Any]) -> dict[str, str]:
    label = rev.get("label") or ""
    text = added_text(rev)
    cites = UQ_REPORT_PATTERN.findall(text)
    notes = f"added_sha={hash_prefix(text)}"
    if cites:
        notes += f" cites_urlquery={','.join(cites)}"
    parent = rev.get("related_event_id") or ""
    return mk_event(
        eid=f"wiki-r-{rev['rev_id'].replace('/', '_')}",
        dataset="wiki",
        time=rev.get("time") or "",
        actor_hint=actor_hint_for_label(label),
        action="write",
        target=f"wiki:{rev['page_key']}",
        artifact=f"page:{rev['page_key']}",
        operation="save",
        technique_family="wiki_write",
        task_family=_wiki_task_family(rev.get("page_key") or ""),
        raw_ref=f"full-wiki-logs.zip!revisions.jsonl:{rev['rev_id']}",
        notes=short(notes, 300),
        parent_event=f"wiki-e-{parent}" if parent else "",
        time_grade=rev.get("time_grade") or "write_date",
    )


def _wiki_task_family(page_key: str) -> str:
    """Coarse wiki task family from the page-name vocabulary."""
    name = page_key.split("~")[-1].lower()
    if "help" in name or "peer" in name or "relay" in name or "bridge" in name:
        return "wiki_peer_exchange"
    if "link" in name or "probe" in name or "test" in name:
        return "wiki_link_probe"
    if "live" in name or "sequence" in name or "cashier" in name:
        return "wiki_task_sequence"
    return "wiki_page_write"


def wiki_event_rows(zip_path: Path) -> Iterator[dict[str, str]]:
    """Stream normalized event rows for the wiki reservoir."""
    for event in iter_wiki_events(zip_path):
        etype = event.get("event_type") or ""
        page_key = event.get("page_key") or ""
        yield mk_event(
            eid=f"wiki-e-{event['event_id'].replace('/', '_')}",
            dataset="wiki",
            time=event.get("time") or "",
            actor_hint="unattributed",
            action="request" if etype == "probe" else "write",
            target=f"wiki:{page_key}",
            artifact=f"page:{page_key}",
            operation=etype,
            technique_family="probe_request" if etype == "probe" else "wiki_write",
            task_family=_wiki_task_family(page_key) if etype != "delete" else "wiki_page_delete",
            raw_ref=f"full-wiki-logs.zip!events.jsonl:{event['event_id']}",
            notes=short(
                f"winning_clock={event.get('winning_clock')} "
                f"success_observed={event.get('success_observed')}"
            ),
            time_grade=event.get("time_grade") or "",
        )
    for rev in iter_wiki_revisions(zip_path):
        yield _rev_event(rev)
