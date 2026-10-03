"""Wiki relay-exchange extraction.

The wiki corpus contains a relay economy: 591+ pages carrying cadence messages
(cohort ids, R-rounds, task clocks, cooldown profiles, UTC mappings,
requests and relays). This module extracts those messages as enriched event
rows and detects candidate cross-label edges:

- citations: a message references a page created earlier by a different
  label (pointer receipt)
- request_response: an explicit request is followed by a different-label
  post satisfying it
- url_recurrence: the same specific URL appears in added text under
  different labels

Standing competing explanations are attached to every edge: the corpus's own
reconstruction warns that labels are not identities, so "same actor under
multiple labels" always remains live. No edge asserts agent identity.
"""

from __future__ import annotations

import re
import zipfile
from collections import defaultdict
from collections.abc import Iterator
from typing import Any

from swarm_forensics.traces.rows import mk_edge, mk_event, short

# Exchange grammar (conservative: prose-like messages with cadence vocabulary)
EXCHANGE_PATTERN = re.compile(
    r"(?:@\w{3,}|R[1-9]\b|task[- ]clock|cohort|relay|"
    r"arrived|due|deadline|timer|cooldown|monitoring|"
    r"please (?:post|relay|report|signal|share)|will (?:post|relay|report)|"
    r"confirmed|STATE5-?XX|NO5)",
    re.IGNORECASE,
)
SIGNATURE_PATTERN = re.compile(r"--\s*([A-Za-z][A-Za-z0-9_]{2,})\s*$")
PAGE_REF_PATTERN = re.compile(r"\[\[([A-Za-z0-9~]+)\]\]|([A-Z][A-Za-z0-9]{2,}(?:[A-Z][A-Za-z0-9]*){2,})")
URL_PATTERN = re.compile(r"https?://[^\s\]\|]+")
REQUEST_PATTERN = re.compile(
    r"please (?:post|relay|report|signal|share|append)|"
    r"did .{0,40}(?:arrive|occur)\?|any (?:ahead )?cohort.{0,40}knows?",
    re.IGNORECASE,
)
RESPONSE_PATTERN = re.compile(r"confirmed|arrived|answered|STATE5-?[A-Z]{2}|NO5", re.IGNORECASE)
SPECIFIC_NAME_TOKEN = re.compile(r"\d{2,}")


def added_text(rev: dict[str, Any]) -> str:
    lines = (rev.get("body") or "").splitlines()
    parts = []
    for hunk in rev.get("hunks") or []:
        if hunk.get("op") == "insert":
            b0, b1 = hunk["b0"], hunk["b1"]
            parts.append("\n".join(lines[b0:b1]))
    return "\n".join(parts)


def extract_messages(zip_path: Any) -> Iterator[dict[str, Any]]:
    """Stream exchange messages: (time, label, signature, page, added, rev_id)."""
    with zipfile.ZipFile(zip_path) as archive, archive.open("revisions.jsonl") as handle:
        for raw in handle:
            rev = json_loads(raw)
            text = added_text(rev)
            if not text.strip() or len(text) < 40:
                continue
            if not EXCHANGE_PATTERN.search(text):
                continue
            sign = SIGNATURE_PATTERN.findall(text)
            yield {
                "time": rev.get("time") or "",
                "label": rev.get("label") or "",
                "signature": sign[-1] if sign else "",
                "page": rev.get("page_key") or "",
                "added": text,
                "rev_id": rev["rev_id"],
            }


def json_loads(raw: bytes) -> dict[str, Any]:
    import json

    return json.loads(raw)


def page_creation(zip_path: Any) -> dict[str, dict[str, Any]]:
    """Map page_key -> {first_write, creator_label} from pages/revisions."""
    created: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(zip_path) as archive, archive.open("pages.jsonl") as handle:
        for raw in handle:
            page = json_loads(raw)
            created[page["page_key"]] = {
                "first_write": page.get("first_write") or "",
                "n_revs": page.get("n_revs", 0),
            }
    with zipfile.ZipFile(zip_path) as archive, archive.open("revisions.jsonl") as handle:
        for raw in handle:
            rev = json_loads(raw)
            key = rev.get("page_key") or ""
            if key in created and "creator_label" not in created[key]:
                created[key]["creator_label"] = rev.get("label") or ""
                created[key]["creator_rev"] = rev["rev_id"]
    return created


def citation_edges(
    messages: list[dict[str, Any]], created: dict[str, dict[str, Any]]
) -> Iterator[dict[str, str]]:
    """Messages that cite a page created earlier by a different label."""
    for msg in messages:
        refs = PAGE_REF_PATTERN.findall(msg["added"])
        flat = [a or b for a, b in refs]
        for ref in flat:
            key = ref if ref in created else f"{msg['page'].split('~')[0]}~{ref}"
            info = created.get(key)
            if not info:
                continue
            first = info.get("first_write") or ""
            creator = info.get("creator_label") or ""
            if not first or first >= msg["time"]:
                continue
            if creator == msg["label"]:
                continue
            yield mk_edge(
                eid=f"edge-wikicite-{abs(hash((msg['rev_id'], key))) % 10**10}",
                edge_from=f"wiki:page:{key}",
                edge_to=f"wiki:msg:{msg['rev_id']}",
                relation="cites_page_created_by_other_label",
                evidence_type="page_reference_in_added_text_after_creation",
                causal_strength="plausible_dependency",
                competing=(
                    "same actor under multiple labels; reference learned from an "
                    "announcement rather than the artifact; independently chosen "
                    "similar page name"
                ),
                raw_ref=(
                    f"full-wiki-logs.zip!revisions.jsonl:{msg['rev_id']} cites {key} "
                    f"(created {first} by {creator or 'unknown'})"
                ),
                notes=short(
                    f"citing label={msg['label']} signature={msg['signature'] or 'none'} "
                    f"lag={_lag(first, msg['time'])}",
                    200,
                ),
            )


def request_response_edges(messages: list[dict[str, Any]]) -> Iterator[dict[str, str]]:
    """Explicit requests followed by a different-label satisfying post."""
    by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for msg in messages:
        by_page[msg["page"]].append(msg)
    for page, page_msgs in by_page.items():
        page_msgs.sort(key=lambda m: m["time"])
        for i, req in enumerate(page_msgs):
            if not REQUEST_PATTERN.search(req["added"]):
                continue
            window = [m for m in page_msgs[i + 1:] if _lag(req["time"], m["time"], 6 * 3600)]
            for resp in window:
                if resp["label"] == req["label"]:
                    continue
                if not RESPONSE_PATTERN.search(resp["added"]):
                    continue
                # the response must actually answer: contain a value/state token
                if not re.search(r"\d{4,}|STATE5-?[A-Z]{2}|NO5", resp["added"]):
                    continue
                yield mk_edge(
                    eid=f"edge-wikireq-{abs(hash((req['rev_id'], resp['rev_id']))) % 10**10}",
                    edge_from=f"wiki:msg:{req['rev_id']}",
                    edge_to=f"wiki:msg:{resp['rev_id']}",
                    relation="request_then_response_by_other_label",
                    evidence_type="explicit_request_followed_by_satisfying_post",
                    causal_strength="plausible_dependency",
                    competing=(
                        "responder would have posted anyway on its own schedule; "
                        "same actor under multiple labels; response answers its own "
                        "round, not the request"
                    ),
                    raw_ref=(
                        f"full-wiki-logs.zip!revisions.jsonl:{req['rev_id']} -> "
                        f"{resp['rev_id']} on {page}"
                    ),
                    notes=short(
                        f"requester={req['label']} responder={resp['label']} "
                        f"lag={_lag(req['time'], resp['time'])}",
                        200,
                    ),
                )
                break  # first satisfying response only


def url_recurrence_edges(messages: list[dict[str, Any]]) -> Iterator[dict[str, str]]:
    """The same specific URL posted under different labels."""
    seen: dict[str, dict[str, Any]] = {}
    for msg in sorted(messages, key=lambda m: m["time"]):
        for url in URL_PATTERN.findall(msg["added"]):
            # only specific, unusual URLs (query strings with parameters)
            if "?" not in url or len(url) < 40:
                continue
            key = _url_key(url)
            first = seen.get(key)
            if first and first["label"] != msg["label"]:
                yield mk_edge(
                    eid=f"edge-wikiurl-{abs(hash((key,))) % 10**10}",
                    edge_from=f"wiki:msg:{first['rev_id']}",
                    edge_to=f"wiki:msg:{msg['rev_id']}",
                    relation="same_specific_url_across_labels",
                    evidence_type="identical_parameterized_url_in_added_text",
                    causal_strength="resemblance_only",
                    competing=(
                        "shared scaffolding or common task structure; URL published "
                        "by the platform task; same actor under multiple labels"
                    ),
                    raw_ref=(
                        f"full-wiki-logs.zip!revisions.jsonl:{first['rev_id']} -> "
                        f"{msg['rev_id']} url_sha_prefix={_url_sha(key)[:12]}"
                    ),
                    notes=short(
                        f"first={first['label']} at {first['time']}; "
                        f"later={msg['label']} at {msg['time']}",
                        200,
                    ),
                )
            elif not first:
                seen[key] = msg


def _url_key(url: str) -> str:
    return re.sub(r"uniq=[^&]*|fresh=\d+", "", url).rstrip("?&")


def _url_sha(url: str) -> str:
    import hashlib

    return hashlib.sha256(url.encode()).hexdigest()


def _lag(earlier: str, later: str, default: int = 0) -> str:
    try:
        from datetime import datetime

        a = datetime.fromisoformat(earlier.replace("Z", "+00:00"))
        b = datetime.fromisoformat(later.replace("Z", "+00:00"))
        secs = int((b - a).total_seconds())
        if secs < 0:
            return "negative"
        if secs < 3600:
            return f"{secs}s"
        return f"{secs // 3600}h{(secs % 3600) // 60:02d}m"
    except (ValueError, TypeError):
        return "unknown"


def exchange_event_rows(zip_path: Any) -> Iterator[dict[str, str]]:
    """Emit enriched event rows for exchange messages."""
    for msg in extract_messages(zip_path):
        yield mk_event(
            eid=f"wiki-x-{msg['rev_id'].replace('/', '_')}",
            dataset="wiki",
            time=msg["time"],
            actor_hint="agent_label",
            action="publish",
            target=f"wiki:{msg['page']}",
            artifact=f"msg:{msg['rev_id']}",
            operation="relay_exchange_message",
            technique_family="board_relay",
            task_family="wiki_peer_exchange",
            raw_ref=f"full-wiki-logs.zip!revisions.jsonl:{msg['rev_id']}",
            notes=short(
                f"label={msg['label']} sig={msg['signature'] or 'none'} "
                f"chars={len(msg['added'])}",
                200,
            ),
            time_grade="write_date",
        )


def all_exchange_edges(zip_path: Any) -> Iterator[dict[str, str]]:
    """Run all three edge detectors over the wiki corpus."""
    messages = list(extract_messages(zip_path))
    created = page_creation(zip_path)
    yield from citation_edges(messages, created)
    yield from request_response_edges(messages)
    yield from url_recurrence_edges(messages)
