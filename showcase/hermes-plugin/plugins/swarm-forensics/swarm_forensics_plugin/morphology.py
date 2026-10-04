"""Validate and sanitize morphology cards received from the discovery pipeline."""

from __future__ import annotations

import json
import math
from typing import Any

from .safety import redact_text, redact_url, taint_prescreen

CANDIDATE_STATUSES = frozenset(
    {"known_variant", "possible_new_morphology", "anomaly", "weak_lead"}
)
EVIDENCE_STRENGTHS = frozenset("e%d" % level for level in range(6))
REVIEW_STATUSES = frozenset({"new", "investigating", "resolved", "dismissed"})
REQUIRED_FIELDS = (
    "candidate_id",
    "candidate_label",
    "status",
    "summary",
    "evidence",
    "first_observed",
    "last_observed",
    "distribution",
    "structural_signature",
    "lexical_signature",
    "nearest_known_morphology",
    "similarity_to_known",
    "novelty",
    "coordination_relevance",
    "evidence_strength",
    "alternative_explanations",
    "missing_evidence",
    "recommended_investigation",
    "source_provenance",
)
MAX_CARD_BYTES = 256_000
MAX_CARD_DEPTH = 12
MAX_CONTAINER_ITEMS = 500
MAX_STRING_LENGTH = 64_000


class MorphologyCardError(ValueError):
    """Raised when an imported card breaks the bounded card contract."""


class MorphologyConflict(ValueError):
    """Raised when an existing candidate ID has different card content."""


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _sanitize(value: Any, depth: int = 0) -> Any:
    if depth > MAX_CARD_DEPTH:
        raise MorphologyCardError("card nesting exceeds the maximum depth")
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MorphologyCardError("card contains a non-finite number")
        return value
    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            raise MorphologyCardError("card string exceeds the maximum length")
        cleaned = redact_text(value)
        if cleaned.startswith(("http://", "https://")):
            cleaned = redact_url(cleaned)
        return cleaned
    if isinstance(value, list):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise MorphologyCardError("card list exceeds the maximum length")
        return [_sanitize(item, depth + 1) for item in value]
    if isinstance(value, dict):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise MorphologyCardError("card object exceeds the maximum field count")
        if any(not isinstance(key, str) or len(key) > 200 for key in value):
            raise MorphologyCardError("card field names MUST be short strings")
        cleaned = {}
        for key, item in value.items():
            sanitized_key = _sanitize(key, depth + 1)
            if sanitized_key in cleaned:
                raise MorphologyCardError("redaction produced duplicate card field names")
            cleaned[sanitized_key] = _sanitize(item, depth + 1)
        return cleaned
    raise MorphologyCardError("card contains an unsupported value type")


def _require_text(card: dict[str, Any], field: str, limit: int) -> str:
    value = card.get(field)
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        message = "%s MUST be a non-empty string up to %d characters" % (field, limit)
        raise MorphologyCardError(message)
    return value


def _require_score(card: dict[str, Any], field: str, allow_none: bool = False) -> None:
    value = card.get(field)
    if allow_none and value is None:
        return
    if isinstance(value, bool):
        raise MorphologyCardError("%s MUST be a number from 0 to 1 or an ordinal" % field)
    if isinstance(value, (int, float)):
        try:
            number = float(value)
        except OverflowError:
            number = math.inf
        if math.isfinite(number) and 0 <= number <= 1:
            return
    elif isinstance(value, str) and value.strip() and len(value) <= 32:
        return
    raise MorphologyCardError("%s MUST be a number from 0 to 1 or an ordinal" % field)


def _require_text_list(card: dict[str, Any], field: str) -> None:
    values = card.get(field)
    if not isinstance(values, list) or len(values) > 100:
        raise MorphologyCardError("%s MUST be a list of at most 100 strings" % field)
    if any(not isinstance(item, str) or len(item) > 2_000 for item in values):
        raise MorphologyCardError("%s MUST contain bounded strings" % field)


def normalize_candidate_card(raw: Any) -> tuple[dict[str, Any], bool]:
    """Validate a candidate card, redact secrets, and report injection markers.

    Preserve unknown JSON fields so dataset-specific provenance survives import.
    """
    if not isinstance(raw, dict):
        raise MorphologyCardError("card MUST be a JSON object")
    try:
        serialized = json.dumps(raw, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError, RecursionError):
        raise MorphologyCardError("card MUST contain strict JSON values") from None
    if len(serialized.encode("utf-8")) > MAX_CARD_BYTES:
        raise MorphologyCardError("card exceeds the maximum size")
    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        raise MorphologyCardError("card is missing required fields: %s" % ", ".join(missing))

    if not isinstance(raw["candidate_id"], str) or not raw["candidate_id"].strip() \
            or len(raw["candidate_id"]) > 200:
        raise MorphologyCardError("candidate_id MUST be a non-empty string up to 200 characters")
    if not isinstance(raw["candidate_label"], str) or not raw["candidate_label"].strip() \
            or len(raw["candidate_label"]) > 240:
        raise MorphologyCardError("candidate_label MUST be a non-empty string up to 240 characters")
    if not isinstance(raw["status"], str) or raw["status"] not in CANDIDATE_STATUSES:
        raise MorphologyCardError("status is not a supported candidate status")
    _require_text(card=raw, field="summary", limit=4_000)
    if not isinstance(raw["evidence"], list) or not raw["evidence"] \
            or len(raw["evidence"]) > 100 \
            or any(not isinstance(item, dict) for item in raw["evidence"]):
        raise MorphologyCardError("evidence MUST be a non-empty list of at most 100 objects")
    for field in ("first_observed", "last_observed"):
        if raw[field] is not None and (not isinstance(raw[field], str) or len(raw[field]) > 100):
            raise MorphologyCardError("%s MUST be a timestamp string or null" % field)
    for field in ("distribution", "structural_signature", "lexical_signature"):
        if not isinstance(raw[field], (dict, list, str)):
            raise MorphologyCardError("%s MUST be an object, list, or string" % field)
    if raw["nearest_known_morphology"] is not None and (
        not isinstance(raw["nearest_known_morphology"], str)
        or len(raw["nearest_known_morphology"]) > 240
    ):
        raise MorphologyCardError("nearest_known_morphology MUST be a string or null")
    _require_score(raw, "similarity_to_known", allow_none=True)
    _require_score(raw, "novelty")
    _require_score(raw, "coordination_relevance")
    if not isinstance(raw["evidence_strength"], str) \
            or raw["evidence_strength"] not in EVIDENCE_STRENGTHS:
        raise MorphologyCardError("evidence_strength MUST be e0 through e5")
    for field in ("alternative_explanations", "missing_evidence"):
        _require_text_list(raw, field)
    recommendations = raw["recommended_investigation"]
    if isinstance(recommendations, str):
        if not recommendations.strip() or len(recommendations) > 4_000:
            raise MorphologyCardError("recommended_investigation MUST contain bounded questions")
    elif isinstance(recommendations, list):
        _require_text_list(raw, "recommended_investigation")
        if not recommendations:
            raise MorphologyCardError("recommended_investigation MUST contain a question")
    else:
        raise MorphologyCardError("recommended_investigation MUST be text or a list of strings")
    provenance = raw["source_provenance"]
    if not isinstance(provenance, (dict, list, str)) or not provenance:
        raise MorphologyCardError("source_provenance MUST identify at least one source")

    card = _sanitize(raw)
    tainted = taint_prescreen(list(_strings(card)))
    return card, tainted
