"""Trajectory mining and 3D goal graph contract.

Defines the payload structures (schema version 2), evidence classes, and validation routines.
Version 2 adds edge claims, a playback timeline, and aggregation notes to version 1.
Diagnostic error messages MUST NOT contain raw record values.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

SCHEMA_VERSION = 2

# Single words an edge label or rule MUST NOT use. The data cannot prove these relations.
FORBIDDEN_RELATIONS = frozenset(
    {"achieved", "completed", "succeeded", "collaborated", "coordinated", "caused", "worked"}
)  # fmt: skip

EVIDENCE_CLASSES = ("recorded", "rule_derived", "inferred")
EvidenceClass = Literal["recorded", "rule_derived", "inferred"]

TIERS = ("agent", "action", "artifact", "goal")
Tier = Literal["agent", "action", "artifact", "goal"]

_MASKS = (
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}"), "Bearer [MASKED]"),
    (re.compile(r"\b(?:hf|sk|ghp|gho|glpat|xox[abpr])[-_][A-Za-z0-9_-]{10,}"), "[MASKED]"),
    (
        re.compile(r"(?i)\b(password|passwd|token|secret|api[_-]?key)(\s*[=:]\s*)(?!\[)[^\s'\"&]+"),
        r"\1\2[MASKED]",
    ),
    (re.compile(r"\b(?!git@)[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"), "[EMAIL]"),
    (re.compile(r"\b(?!127\.0\.0\.1\b)(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP]"),
)


# One trigger tuple per mask. None means: use the digit-dot pre-check (IP mask).
_TRIGGERS = (
    ("bearer",),
    ("hf-", "hf_", "sk-", "sk_", "ghp-", "ghp_", "gho-", "gho_", "glpat-", "glpat_", "xox"),
    ("password", "passwd", "token", "secret", "api"),
    ("@",),
    None,
)
_DIGIT_DOT = re.compile(r"\d\.\d")


class ContractError(Exception):
    """Raised when a data structure violates the contract.

    Error messages MUST NOT include record values.
    """

    def __init__(self, subject: str, reason: str, path: str | None = None):
        self.subject = subject
        self.reason = reason
        self.path = path
        parts = [subject]
        if path:
            parts.append(path)
        parts.append(reason)
        super().__init__(": ".join(parts))


def sanitize_text(value: Any, limit: int = 2400) -> str:
    """Mask credentials and limit character length."""
    text = value if isinstance(value, str) else ""
    if not text:
        return ""
    low = text.lower()
    for (pattern, replacement), triggers in zip(_MASKS, _TRIGGERS, strict=True):
        # Cheap substring pre-check. Each trigger is a necessary condition.
        if triggers is not None and not any(item in low for item in triggers):
            continue
        if triggers is None and not _DIGIT_DOT.search(text):
            continue
        text = pattern.sub(replacement, text)
        low = text.lower()
    if len(text) > limit:
        return f"{text[:limit]}\n[truncated: {len(text) - limit} characters omitted]"
    return text


def parse_utc_timestamp(value: str) -> datetime:
    """Parse UTC timestamp without zone suffix."""
    if not isinstance(value, str) or not value.strip():
        raise ContractError("timestamp", "timestamp is empty or not a string")
    try:
        base, _, fraction = value.partition(".")
        moment = datetime.strptime(f"{base}+0000", "%Y-%m-%d %H:%M:%S%z")
        micro = int(fraction.ljust(6, "0")[:6]) if fraction else 0
        return moment.replace(microsecond=micro).astimezone(timezone.utc)
    except (ValueError, AttributeError):
        raise ContractError("timestamp", "unreadable timestamp format") from None


def format_iso(moment: datetime) -> str:
    """Format datetime as ISO 8601 UTC string."""
    return moment.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


@dataclass
class SourceRef:
    table: str
    row_id: str | int

    def to_dict(self) -> dict[str, Any]:
        return {"table": self.table, "row_id": str(self.row_id)}


@dataclass
class GraphNode:
    id: str
    tier: Tier
    label: str
    source_ref: SourceRef
    claims: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tier": self.tier,
            "label": self.label,
            "source_ref": self.source_ref.to_dict(),
            "claims": self.claims,
            "metadata": self.metadata,
        }


@dataclass
class GraphEdge:
    source: str
    target: str
    evidence_class: EvidenceClass
    rule: str
    source_ref: SourceRef
    score: float = 1.0
    label: str = ""
    claims: list[dict[str, str]] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "evidence_class": self.evidence_class,
            "rule": self.rule,
            "source_ref": self.source_ref.to_dict(),
            "score": self.score,
            "label": self.label,
            "claims": self.claims,
            "note": self.note,
        }


def validate_source_ref(ref: Any, path: str) -> None:
    if not isinstance(ref, dict):
        raise ContractError("source_ref", "must be an object", path)
    if "table" not in ref or not isinstance(ref["table"], str) or not ref["table"]:
        raise ContractError("source_ref", "missing or empty table", f"{path}.table")
    if "row_id" not in ref or ref["row_id"] is None or str(ref["row_id"]) == "":
        raise ContractError("source_ref", "missing or empty row_id", f"{path}.row_id")


def validate_node(node: Any, index: int) -> None:
    path = f"nodes[{index}]"
    if not isinstance(node, dict):
        raise ContractError("node", "must be an object", path)
    for field_name in ("id", "tier", "label", "source_ref"):
        if field_name not in node:
            raise ContractError("node", f"missing required field {field_name}", f"{path}.{field_name}")
    if node["tier"] not in TIERS:
        raise ContractError("node", "invalid tier value", f"{path}.tier")
    validate_source_ref(node["source_ref"], f"{path}.source_ref")
    for claim_idx, claim in enumerate(node.get("claims", [])):
        cpath = f"{path}.claims[{claim_idx}]"
        if not isinstance(claim, dict) or "field_path" not in claim or "text" not in claim:
            raise ContractError("claim", "must contain field_path and text", cpath)


def validate_edge(edge: Any, index: int, valid_nodes: set[str]) -> None:
    path = f"edges[{index}]"
    if not isinstance(edge, dict):
        raise ContractError("edge", "must be an object", path)
    for field_name in ("source", "target", "evidence_class", "rule", "source_ref"):
        if field_name not in edge:
            raise ContractError("edge", f"missing required field {field_name}", f"{path}.{field_name}")
    if edge["evidence_class"] not in EVIDENCE_CLASSES:
        raise ContractError("edge", "invalid evidence_class", f"{path}.evidence_class")
    if edge["source"] not in valid_nodes:
        raise ContractError("edge", "source node not found in nodes list", f"{path}.source")
    if edge["target"] not in valid_nodes:
        raise ContractError("edge", "target node not found in nodes list", f"{path}.target")
    validate_source_ref(edge["source_ref"], f"{path}.source_ref")
    for key in ("label", "rule"):
        words = set(re.split(r"[^a-z]+", str(edge.get(key, "")).lower()))
        if words & FORBIDDEN_RELATIONS:
            raise ContractError("edge", "label asserts an unproven relation", f"{path}.{key}")
    for claim_idx, claim in enumerate(edge.get("claims", [])):
        if not isinstance(claim, dict) or "field_path" not in claim or "text" not in claim:
            raise ContractError("claim", "must contain field_path and text", f"{path}.claims[{claim_idx}]")


def validate_trajectory_payload(payload: Any) -> None:
    """Validate full 3D goal graph payload."""
    if not isinstance(payload, dict):
        raise ContractError("payload", "must be a dictionary")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("payload", "unsupported or missing schema_version", "schema_version")
    if "nodes" not in payload or not isinstance(payload["nodes"], list):
        raise ContractError("payload", "missing nodes list", "nodes")
    if "edges" not in payload or not isinstance(payload["edges"], list):
        raise ContractError("payload", "missing edges list", "edges")

    node_ids: set[str] = set()
    for idx, node in enumerate(payload["nodes"]):
        validate_node(node, idx)
        node_id = node["id"]
        if node_id in node_ids:
            raise ContractError("payload", "duplicate node id", f"nodes[{idx}].id")
        node_ids.add(node_id)

    for idx, edge in enumerate(payload["edges"]):
        validate_edge(edge, idx, node_ids)
