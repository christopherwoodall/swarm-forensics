"""Shared event and edge schema for stage-4 trace-reservoir forensics.

Every row is one observable. No row asserts an agent identity, a successful
remote effect, or a causal transfer. Rows carry the competing explanation and
the raw reference, so later passes cannot silently upgrade evidence levels.
"""

from __future__ import annotations

from typing import Any

EVENT_FIELDS: tuple[str, ...] = (
    "event_id",
    "dataset",
    "time",
    "time_grade",
    "actor_hint",
    "action",
    "target",
    "artifact",
    "operation",
    "parent_event",
    "observed_read",
    "behavior_change",
    "technique_family",
    "task_family",
    "raw_ref",
    "confidence",
    "notes",
)

EDGE_FIELDS: tuple[str, ...] = (
    "edge_id",
    "edge_from",
    "edge_to",
    "relation",
    "evidence_type",
    "causal_strength",
    "competing_explanation",
    "raw_ref",
    "notes",
)

EVENT_ACTIONS: tuple[str, ...] = (
    "request",       # an outbound request attempt is encoded or logged
    "write",         # durable content was written to a shared substrate
    "read",          # a durable artifact was retrieved or requested
    "publish",       # an artifact was made available to possible readers
    "register",     # a registry object was created (package, account, alias)
)

EDGE_STRENGTHS: tuple[str, ...] = (
    "observed_causal_dependency",
    "strongly_supported_dependency",
    "plausible_dependency",
    "temporal_structural_association_only",
    "resemblance_only",
)

DATASETS: tuple[str, ...] = (
    "urlquery",
    "arquivo",
    "rubygems",
    "wiki",
)

TECHNIQUE_FAMILIES: tuple[str, ...] = (
    "relay_fetch",            # markdown.new, r.jina.ai, allorigins, cors proxies
    "keyless_publish",        # no-auth write surfaces (pastebins, hosting)
    "shortener_c2",           # URL shorteners as durable alias tables
    "relay_indirection",      # httpbin redirect chains, markdown.new relays
    "answer_table_publish",   # base64 answer tables through public hosts
    "probe_request",          # connectivity/protocol probes
    "wiki_write",             # wiki edits and coordination pages
    "board_relay",            # message-board style exchange on wikis
    "env_feedback",           # behavior change after response-visible state
    "nonce_grammar",          # zz= nonces, epoch-nonce names, marker values
    "shared_relay",           # same relay URL used across datasets
    "registry_abuse",         # package registry as storage/exfil channel
    "no_visible_mechanism",   # row parsed clean; no coordination-relevant mechanism visible
    "content_not_in_release", # the released record withholds request shape/content
    "unknown",                # not yet examined; reserved for future passes
)

VALID_ACTOR_HINTS: tuple[str, ...] = (
    "investigator",   # record provenance is the public investigation itself
    "human",          # human edit or human-authored trace
    "agent_label",    # a self-assigned agent-style name is present
    "unattributed",   # no identity signal in the record
)


class TraceError(ValueError):
    """A trace row broke the stage-4 schema contract."""


def validate_event(row: dict[str, Any]) -> list[str]:
    """Return every reason this event row breaks the contract.

    Optional-text fields (parent_event, notes, artifact) may be empty.
    """
    problems: list[str] = []
    for key in EVENT_FIELDS:
        if key not in row or not _isstr(row[key]):
            problems.append(f"event field {key} must be a string")
        elif key == "event_id" and row[key] == "":
            problems.append("event_id must be non-empty")
    if problems:
        return problems
    if row["dataset"] not in DATASETS:
        problems.append(f"dataset must be one of {DATASETS}")
    if row["action"] not in EVENT_ACTIONS:
        problems.append(f"action must be one of {EVENT_ACTIONS}")
    if row["technique_family"] not in TECHNIQUE_FAMILIES:
        problems.append(f"technique_family must be one of {TECHNIQUE_FAMILIES}")
    if row["actor_hint"] not in VALID_ACTOR_HINTS:
        problems.append(f"actor_hint must be one of {VALID_ACTOR_HINTS}")
    return problems


def validate_edge(row: dict[str, Any]) -> list[str]:
    """Return every reason this edge row breaks the contract.

    Optional-text fields (notes) may be empty.
    """
    problems: list[str] = []
    for key in EDGE_FIELDS:
        if key not in row or not _isstr(row[key]):
            problems.append(f"edge field {key} must be a string")
    if problems:
        return problems
    if row["causal_strength"] not in EDGE_STRENGTHS:
        problems.append(f"causal_strength must be one of {EDGE_STRENGTHS}")
    return problems


def _isstr(value: Any) -> bool:
    return isinstance(value, str)
