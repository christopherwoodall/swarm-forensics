"""Shared row constructors for stage-4 trace normalization."""

from __future__ import annotations

import hashlib
import re
from typing import Any

EPOCH_NAME_PATTERN = re.compile(r"(17[89]\d{8})")
ZZ_PATTERN = re.compile(r"zz=([0-9A-Za-z]+)")
INVESTIGATOR_LABELS = frozenset(
    {"ResearchUser", "ResearchQux", "ResearchTesterX", "ResearchOur"}
)


def short(text: Any, limit: int = 300) -> str:
    """Flatten and truncate free text for the notes column."""
    text = (text or "").replace("\n", " ").replace("\r", " ")
    return str(text)[:limit]


def hash_prefix(text: str, limit: int = 12) -> str:
    digest = hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()
    return digest[:limit]


def mk_event(
    eid: str,
    dataset: str,
    time: str,
    actor_hint: str,
    action: str,
    target: str,
    artifact: str,
    operation: str,
    technique_family: str,
    raw_ref: str,
    notes: str = "",
    parent_event: str = "",
    observed_read: str = "unobserved",
    behavior_change: str = "none_observed",
    confidence: str = "high",
    time_grade: str = "service_timestamp",
) -> dict[str, str]:
    """Build one normalized event row."""
    row = {
        "event_id": eid,
        "dataset": dataset,
        "time": time,
        "time_grade": time_grade,
        "actor_hint": actor_hint,
        "action": action,
        "target": target,
        "artifact": artifact,
        "operation": operation,
        "parent_event": parent_event,
        "observed_read": observed_read,
        "behavior_change": behavior_change,
        "technique_family": technique_family,
        "raw_ref": raw_ref,
        "confidence": confidence,
        "notes": notes,
    }
    return row


def mk_edge(
    eid: str,
    edge_from: str,
    edge_to: str,
    relation: str,
    evidence_type: str,
    causal_strength: str,
    competing: str,
    raw_ref: str,
    notes: str = "",
) -> dict[str, str]:
    """Build one candidate edge row."""
    return {
        "edge_id": eid,
        "edge_from": edge_from,
        "edge_to": edge_to,
        "relation": relation,
        "evidence_type": evidence_type,
        "causal_strength": causal_strength,
        "competing_explanation": competing,
        "raw_ref": raw_ref,
        "notes": notes,
    }


def added_text(rev: dict[str, Any]) -> str:
    """Reconstruct only the text a revision added, from its hunks."""
    lines = (rev.get("body") or "").splitlines()
    parts = []
    for hunk in rev.get("hunks") or []:
        if hunk.get("op") == "insert":
            parts.append("\n".join(lines[hunk["b0"]:hunk["b1"]]))
    return "\n".join(parts)


def actor_hint_for_label(label: str) -> str:
    """Map a wiki label to an actor hint, investigator labels excluded."""
    if not label:
        return "unattributed"
    if label in INVESTIGATOR_LABELS:
        return "investigator"
    if re.match(r"^(?:Agent|OpenAI|Data[A-Z]|Research|Diligent|Archive|Cashier)", label):
        return "agent_label"
    return "unattributed"
