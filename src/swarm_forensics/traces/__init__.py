"""Stage 4 trace-reservoir forensics.

Normalize external trace reservoirs (URLQuery, Arquivo.pt, RubyGems/wiki
collusion) into one cross-dataset event table and candidate edge table.

The governing protocol lives at
colette-research/hermes-research/stage-4-trace-reservoirs/PROTOCOL.md.
"""

from swarm_forensics.traces.schema import (
    EDGE_FIELDS,
    EDGE_STRENGTHS,
    EVENT_ACTIONS,
    EVENT_FIELDS,
    VALID_ACTOR_HINTS,
    validate_edge,
    validate_event,
)

__all__ = [
    "EDGE_FIELDS",
    "EDGE_STRENGTHS",
    "EVENT_ACTIONS",
    "EVENT_FIELDS",
    "VALID_ACTOR_HINTS",
    "validate_edge",
    "validate_event",
]
