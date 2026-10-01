"""Export one computer-use session as an evidence-linked replay case.

Usage:
    python -m swarm_forensics.replay --mock [--out PATH]
    python -m swarm_forensics.replay --session UUID [--dir data/raw] [--out PATH]

The exporter streams each archive one line at a time. It keeps only the selected session
and bounded related context. Text fields are masked and length-limited. Upstream
`[REDACTED]` markers stay in place. Error messages MUST NOT contain record values.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import zlib
from collections import Counter
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

SCHEMA_VERSION = 1
CLASSIFICATION = "village_activity"
CLASSIFICATION_NOTE = "Recorded village activity. Not a verified attack."
DEFAULT_DIR = Path("data/raw")
DEFAULT_OUT_DIR = Path("data/raw/replay")
MOCK_OUT = DEFAULT_OUT_DIR / "sample-case.json"

MAX_STEPS = 2000
MAX_CONTEXT_EVENTS = 200
MAX_GOAL_CHARS = 4000
MAX_COMMAND_CHARS = 2400
MAX_OUTPUT_CHARS = 2400
MAX_CLAIM_CHARS = 600
MAX_HOSTS_PER_STEP = 8

STATUSES = ("stderr_recorded", "output_recorded", "no_output")
RELATIONS = ("requested", "referenced")
LINKS = ("session_id", "time_window")

SURFACES = {
    "shell": "Shell",
    "desktop": "Desktop input",
    "chat": "Chat",
    "history": "History search",
    "request": "Village request",
    "idle": "Pause or wait",
    "other": "Other action",
}
WORK = {
    "git-push": "Git push attempt",
    "http": "HTTP request command",
    "file-write": "File write syntax",
    "python": "Python",
    "shell": "Other shell command",
    "desktop": "Desktop input",
    "chat": "Chat message",
    "search": "History search",
    "request": "Village request",
    "idle": "Pause or wait",
    "other": "Other action",
}
_WORK_PRIORITY = ("git-push", "http", "file-write", "python")
_SIGNALS = {
    "python": re.compile(r"\bpython[0-9.]*\b"),
    "file-write": re.compile(r"write_text\s*\(|\.write\s*\(|\bcat\s+[^\n]*>|<<\s*['\"]?\w+"),
    "http": re.compile(r"\b(?:curl|wget)\b|requests\.(?:get|post|put|delete)\s*\("),
    "git-push": re.compile(r"\bgit\s+push\b"),
}
_FETCH = re.compile(
    r"\b(?:curl|wget)\b|requests\.(?:get|post|put|delete)\s*\(|urllib|"
    r"\bgit\s+(?:push|pull|clone|fetch)\b"
)
_DESKTOP = {
    "mouse_move", "left_click", "right_click", "middle_click", "double_click",
    "triple_click", "left_click_drag", "left_mouse_down", "left_mouse_up", "key", "type",
    "hold_key", "scroll", "screenshot", "cursor_position", "view_clipboard",
    "get_pixel_coords_of_element",
}  # fmt: skip
_REQUESTS = {
    "request_human_helper", "request_Google_sign_in",
    "request_approval_for_unsolicited_outreach",
}  # fmt: skip
_TEXT_OMITTED = {"type", "key", "hold_key"}
_DETAIL_KEYS = ("coordinate", "seconds", "scrollDirection", "scrollAmount", "roomName", "restart")
_PROVIDERS = (
    (("gpt", "o1", "o3", "o4", "o5"), "OpenAI"),
    (("claude",), "Anthropic"),
    (("gemini",), "Google"),
    (("kimi",), "Moonshot"),
    (("grok",), "xAI"),
    (("deepseek",), "DeepSeek"),
    (("glm", "z-ai"), "Zhipu"),
    (("meta", "muse"), "Meta"),
)
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
_URL = re.compile(r"https?://([^/\s<>'\"\\?#]+)", re.IGNORECASE)
_HOST = re.compile(r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z][a-z0-9-]*")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


class ReplayError(Exception):
    """Raised for a failed export or contract check. The message MUST NOT hold record values."""

    def __init__(self, subject: str, reason: str, path: str | None = None):
        self.subject = subject
        self.reason = reason
        self.path = path
        parts = [subject] + ([path] if path else []) + [reason]
        super().__init__(": ".join(parts))


class Clean(NamedTuple):
    text: str
    omitted: int  # characters removed by the length limit
    masked: int  # values replaced by a mask
    markers: int  # upstream [REDACTED] markers kept in the text


def sanitize(value: Any, limit: int) -> Clean:
    """Mask credential-like values and cut the text to `limit` characters."""
    text = value if isinstance(value, str) else ""
    markers = text.count("[REDACTED]")
    masked = 0
    for pattern, replacement in _MASKS:
        text, count = pattern.subn(replacement, text)
        masked += count
    omitted = max(0, len(text) - limit)
    if omitted:
        text = f"{text[:limit]}\n[truncated: {omitted} characters omitted]"
    return Clean(text, omitted, masked, markers)


def parse_timestamp(value: str) -> datetime:
    """Parse a dataset timestamp (UTC, 1-6 fractional digits, no zone suffix)."""
    try:
        base, _, fraction = value.partition(".")
        moment = datetime.strptime(f"{base}+0000", "%Y-%m-%d %H:%M:%S%z")
        micro = int(fraction.ljust(6, "0")[:6]) if fraction else 0
        return moment.replace(microsecond=micro).astimezone(timezone.utc)
    except (ValueError, AttributeError):
        raise ReplayError("timestamp", "unreadable value") from None


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def provider_of(model: str) -> str:
    """Group a model name under a provider label. This is a naming heuristic only."""
    lowered = model.lower().removeprefix("claude-code::")
    for prefixes, label in _PROVIDERS:
        if lowered.startswith(prefixes):
            return label
    return "Other"


def hosts_in(text: str) -> list[str]:
    """Return public host names that appear in URLs. IP addresses are skipped."""
    found: dict[str, None] = {}
    for raw in _URL.findall(text):
        host = raw.rsplit("@", 1)[-1].split(":")[0].lower().rstrip(".,;)")
        if _HOST.fullmatch(host):
            found.setdefault(host)
    return list(found)[:MAX_HOSTS_PER_STEP]


def _classify(action: dict[str, Any]) -> tuple[str, str, str]:
    """Return (action_type, surface id, base work id) for one recorded action."""
    if "command" in action:
        return "shell_command", "shell", "shell"
    name = str(action.get("action") or "")
    if not name:
        return "none", "other", "other"
    if name in _DESKTOP:
        return name, "desktop", "desktop"
    if name in ("pause", "wait"):
        return name, "idle", "idle"
    if name in ("send_message_back_to_chat", "move_to_room"):
        return name, "chat", "chat"
    if name == "search_history":
        return name, "history", "search"
    if name in _REQUESTS:
        return name, "request", "request"
    return name, "other", "other"


def _status(turn: dict[str, Any]) -> tuple[str, str]:
    if turn.get("error"):
        return "stderr_recorded", "Text was stored in the error (stderr) field. It does not prove failure."
    if turn.get("output"):
        return "output_recorded", "Output was recorded. Success is not established."
    return "no_output", "No output was recorded. The outcome is unknown."


def step_from_turn(turn: dict[str, Any], session_id: str, agent_id: str) -> dict[str, Any]:
    """Build one replay step from one `computer_use_turns` record."""
    raw_action = turn.get("agent_action")
    action = raw_action if isinstance(raw_action, dict) else {}
    action_type, surface, work = _classify(action)
    command = action.get("command") if isinstance(action.get("command"), str) else ""
    signals = [name for name in _WORK_PRIORITY if _SIGNALS[name].search(command)]
    if surface == "shell" and signals:
        work = signals[0]
    status, note = _status(turn)

    cmd = sanitize(command, MAX_COMMAND_CHARS)
    out = sanitize(turn.get("output"), MAX_OUTPUT_CHARS)
    err = sanitize(turn.get("error"), MAX_OUTPUT_CHARS)
    claim = None
    if action_type == "send_message_back_to_chat":
        claim = sanitize(action.get("content"), MAX_CLAIM_CHARS)
    elif action_type == "search_history":
        claim = sanitize(action.get("query"), MAX_CLAIM_CHARS)
    cleans = [cmd, out, err] + ([claim] if claim else [])

    detail = {k: action[k] for k in _DETAIL_KEYS if action.get(k) is not None}
    if action_type in _TEXT_OMITTED and action.get("text"):
        detail["text"] = "omitted: typed or key input is not exported"
    relation = "requested" if _FETCH.search(command) else "referenced"
    first_line = next((line for line in cmd.text.splitlines() if line.strip()), "")
    summary = first_line[:100] if surface == "shell" else action_type.replace("_", " ")
    truncated = [
        name
        for name, clean in (("command", cmd), ("output", out), ("error", err), ("claim", claim))
        if clean and clean.omitted
    ]
    return {
        "i": 0,
        "ts": turn["created_at"],
        "t_ms": 0,
        "source": {"table": "computer_use_turns", "id": turn["id"]},
        "actor": agent_id,
        "session_id": session_id,
        "action_type": action_type,
        "surface": surface,
        "work": work,
        "signals": [WORK[name] for name in signals],
        "summary": summary,
        "detail": detail,
        "command": cmd.text or None,
        "output": out.text or None,
        "error": err.text or None,
        "claim": claim.text if claim and claim.text else None,
        "status": status,
        "outcome_note": note,
        "destinations": [{"host": h, "relation": relation} for h in hosts_in(command)],
        "evidence": {
            "truncated": truncated,
            "masked_values": sum(c.masked for c in cleans),
            "upstream_redactions": sum(c.markers for c in cleans),
            "screenshot_redacted": bool(turn.get("screenshot_is_redacted")),
        },
    }


def context_from_event(event: dict[str, Any], link: str) -> dict[str, Any]:
    """Build one contextual entry from one `events` record."""
    data = event.get("data") if isinstance(event.get("data"), dict) else {}
    kind = str(data.get("actionType") or "unknown")
    text = None
    omitted = 0
    if kind == "AGENT_TALK":
        clean = sanitize(data.get("content"), MAX_CLAIM_CHARS)
        text, omitted = clean.text or None, clean.omitted
    elif kind == "PAUSE" and data.get("seconds") is not None:
        text = f"{data['seconds']} seconds"
    return {
        "source": {"table": "events", "id": event["id"], "event_index": event.get("event_index")},
        "ts": event["created_at"],
        "action_type": kind,
        "link": link,
        "text": text,
        "truncated": bool(omitted),
    }


def assemble_case(
    session: dict[str, Any],
    agent: dict[str, Any],
    turns: list[dict[str, Any]],
    events: list[tuple[dict[str, Any], str]],
    synthetic: bool = False,
) -> dict[str, Any]:
    """Join session, agent, turns, and events into one validated case."""
    ordered = sorted(turns, key=lambda t: (t["created_at"], t["id"]))
    dropped = max(0, len(ordered) - MAX_STEPS)
    steps = [step_from_turn(t, session["id"], agent["id"]) for t in ordered[:MAX_STEPS]]
    if not steps:
        raise ReplayError("session", "no recorded turns")
    first = parse_timestamp(steps[0]["ts"])
    for number, step in enumerate(steps, start=1):
        moment = parse_timestamp(step["ts"])
        step["i"] = number
        step["t_ms"] = int((moment - first).total_seconds() * 1000)
        step["ts"] = iso(moment)
    context = sorted(
        (context_from_event(e, link) for e, link in events),
        key=lambda c: (c["ts"], c["source"]["event_index"] or 0, c["source"]["id"]),
    )
    context_dropped = max(0, len(context) - MAX_CONTEXT_EVENTS)
    for entry in context:
        entry["ts"] = iso(parse_timestamp(entry["ts"]))
    goal = sanitize(session.get("session_goal"), MAX_GOAL_CHARS)
    model = str(agent.get("model_string") or "unknown")
    notes = [
        "Steps are recorded actions. A command that ran does not prove a successful result.",
        "Context events are labeled by link. Time-window events are not causal evidence.",
        "Provider grouping uses the model name. It does not imply organizational control.",
    ]
    case = {
        "schema_version": SCHEMA_VERSION,
        "case_id": f"session-{session['id'][:8]}",
        "title": "Synthetic example workflow" if synthetic else "AI Village session replay",
        "classification": CLASSIFICATION,
        "classification_note": CLASSIFICATION_NOTE,
        "synthetic": synthetic,
        "source": {
            "dataset": "aidigestorg/ai-village",
            "tables": ["computer_use_sessions", "computer_use_turns", "agents", "events"],
            "session_id": session["id"],
        },
        "actor": {
            "agent_id": agent["id"],
            "model": model,
            "provider": provider_of(model),
            "provider_basis": "model_string prefix",
        },
        "session": {
            "id": session["id"],
            "created_at": iso(parse_timestamp(session["created_at"])),
            "goal": goal.text,
            "goal_truncated": bool(goal.omitted),
            "stop_requested": bool(session.get("has_been_asked_to_stop")),
        },
        "legend": {"surfaces": SURFACES, "work": WORK},
        "steps": steps,
        "context": context[:MAX_CONTEXT_EVENTS],
        "limits": {
            "turns_dropped": dropped,
            "context_dropped": context_dropped,
            "truncated_fields": sum(len(s["evidence"]["truncated"]) for s in steps),
            "masked_values": sum(s["evidence"]["masked_values"] for s in steps) + goal.masked,
            "notes": notes,
        },
    }
    validate_case(case)
    return case


def _fail(path: str, reason: str) -> None:
    raise ReplayError("case", reason, path)


def _require(obj: Any, path: str, keys: tuple[str, ...]) -> None:
    if not isinstance(obj, dict):
        _fail(path, "must be an object")
    for key in keys:
        if key not in obj:
            _fail(f"{path}.{key}", "required field is missing")


def validate_case(case: Any) -> None:
    """Raise ReplayError when `case` breaks the replay contract."""
    top = ("schema_version", "case_id", "classification", "source", "actor", "session")
    _require(case, "$", top + ("legend", "steps", "context", "limits"))
    if case["schema_version"] != SCHEMA_VERSION:
        _fail("$.schema_version", "unsupported version")
    if case["classification"] != CLASSIFICATION:
        _fail("$.classification", "unsupported classification")
    _require(case["actor"], "$.actor", ("agent_id", "model", "provider"))
    _require(case["session"], "$.session", ("id", "created_at", "goal"))
    steps = case["steps"]
    if not isinstance(steps, list) or not steps:
        _fail("$.steps", "must be a non-empty list")
    step_keys = ("i", "ts", "t_ms", "source", "actor", "session_id", "action_type", "surface")
    step_keys += ("work", "status", "outcome_note", "destinations", "evidence")
    seen: set[str] = set()
    previous = 0
    for index, step in enumerate(steps):
        path = f"$.steps[{index}]"
        _require(step, path, step_keys)
        _require(step["source"], f"{path}.source", ("table", "id"))
        if step["i"] != index + 1:
            _fail(f"{path}.i", "steps must be numbered from 1 without gaps")
        if step["status"] not in STATUSES:
            _fail(f"{path}.status", "unknown status")
        if step["surface"] not in case["legend"]["surfaces"]:
            _fail(f"{path}.surface", "surface is missing from the legend")
        if step["work"] not in case["legend"]["work"]:
            _fail(f"{path}.work", "work type is missing from the legend")
        if step["source"]["id"] in seen:
            _fail(f"{path}.source.id", "duplicate source record")
        seen.add(step["source"]["id"])
        if step["t_ms"] < previous:
            _fail(f"{path}.t_ms", "steps must be in time order")
        previous = step["t_ms"]
        for number, dest in enumerate(step["destinations"]):
            if dest.get("relation") not in RELATIONS or not dest.get("host"):
                _fail(f"{path}.destinations[{number}]", "invalid destination")
    for index, entry in enumerate(case["context"]):
        path = f"$.context[{index}]"
        _require(entry, path, ("source", "ts", "action_type", "link"))
        if entry["link"] not in LINKS:
            _fail(f"{path}.link", "unknown link")


def _stream(path: Path, table: str) -> Iterator[str]:
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            yield from handle
    except FileNotFoundError:
        raise ReplayError(table, "file not found") from None
    except (OSError, EOFError, zlib.error, UnicodeDecodeError):
        raise ReplayError(table, "damaged or unreadable gzip archive") from None


def _records(path: Path, table: str, needles: tuple[str, ...]) -> Iterator[dict[str, Any]]:
    """Yield records whose line contains a needle. Parse one line at a time."""
    for number, line in enumerate(_stream(path, table), start=1):
        if not any(needle in line for needle in needles):
            continue
        try:
            record = json.loads(line)
        except ValueError:
            raise ReplayError(table, f"malformed JSON on line {number}") from None
        if isinstance(record, dict):
            yield record


def export_session(session_id: str, directory: Path = DEFAULT_DIR) -> dict[str, Any]:
    """Stream the archives in `directory` and return the case for one session."""
    if not _UUID.fullmatch(session_id):
        raise ReplayError("session", "id must be a lowercase UUID")
    table = "computer_use_sessions"
    session = next(
        (r for r in _records(directory / f"{table}.jsonl.gz", table, (session_id,))
         if r.get("id") == session_id),
        None,
    )  # fmt: skip
    if session is None:
        raise ReplayError("session", "not found in computer_use_sessions")
    agent_id = session["agent_id"]
    agent = next(
        (r for r in _records(directory / "agents.jsonl.gz", "agents", (agent_id,))
         if r.get("id") == agent_id),
        {"id": agent_id, "model_string": "unknown"},
    )  # fmt: skip
    turns = [
        r
        for r in _records(directory / "computer_use_turns.jsonl.gz", "computer_use_turns", (session_id,))
        if r.get("session_id") == session_id
    ]
    if not turns:
        raise ReplayError("session", "no recorded turns")
    start = session["created_at"]
    end = max(t["created_at"] for t in turns)
    events: list[tuple[dict[str, Any], str]] = []
    for record in _records(directory / "events.jsonl.gz", "events", (session_id, agent_id)):
        data = record.get("data") if isinstance(record.get("data"), dict) else {}
        if data.get("computerUseSessionId") == session_id:
            events.append((record, "session_id"))
        elif agent_id in (data.get("agentId"), data.get("speakerId")) and (
            start <= record.get("created_at", "") <= end
        ):
            events.append((record, "time_window"))
    return assemble_case(session, agent, turns, events)


def _mock_turn(n: int, seconds: int, action: dict[str, Any] | None, **extra: Any) -> dict[str, Any]:
    stamp = f"2026-01-01 10:{seconds // 60:02d}:{seconds % 60:02d}.{n:03d}"
    return {"id": f"mock-turn-{n:02d}", "created_at": stamp, "agent_action": action, **extra}


def build_mock_case() -> dict[str, Any]:
    """Return a deterministic synthetic case. It uses the same code path as real exports."""
    agent = {"id": "mock-agent-01", "model_string": "gpt-mock-1"}
    session = {
        "id": "00000000-0000-4000-8000-000000000001",
        "created_at": "2026-01-01 10:00:00.000",
        "session_goal": "Synthetic goal: fetch a public status page, write a summary, and push it.",
        "has_been_asked_to_stop": False,
    }
    turns = [
        _mock_turn(1, 0, {"action": "mouse_move", "coordinate": [10, 20]}),
        _mock_turn(2, 5, {"command": "curl -s https://example.org/status"}, output="ok"),
        _mock_turn(3, 20, {"command": "python3 summarize.py"}, output="done"),
        _mock_turn(
            4, 35, {"command": "cat > notes.md <<'EOF'\nsummary\nEOF"}, output="",
        ),
        _mock_turn(5, 50, {"action": "pause", "seconds": 30}),
        _mock_turn(
            6, 80, {"action": "send_message_back_to_chat", "content": "Summary ready."},
        ),
        _mock_turn(
            7, 95, {"command": "git push origin main  # token=abcd1234efgh5678"},
            error="remote: permission denied (contact admin@example.org at 10.1.2.3)",
        ),
        _mock_turn(8, 110, {"action": "search_history", "query": "previous push errors"}),
        _mock_turn(
            9, 125, {"command": "git push origin main"}, output="Everything up-to-date",
        ),
    ]
    events = [
        (
            {
                "id": "mock-event-01",
                "event_index": 1,
                "created_at": "2026-01-01 10:01:30.000",
                "data": {"actionType": "AGENT_TALK", "content": "Unrelated chat in this window."},
            },
            "time_window",
        ),
        (
            {
                "id": "mock-event-02",
                "event_index": 2,
                "created_at": "2026-01-01 10:02:10.000",
                "data": {"actionType": "CONSOLIDATE", "computerUseSessionId": session["id"]},
            },
            "session_id",
        ),
    ]
    return assemble_case(session, agent, turns, events, synthetic=True)


def write_case(case: dict[str, Any], out: Path) -> None:
    """Validate and write a case. The path MUST be under an ignored directory."""
    validate_case(case)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(case, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--mock", action="store_true", help="write the synthetic case (offline)")
    group.add_argument("--session", metavar="UUID", help="export one real session")
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="default: data/raw")
    parser.add_argument("--out", type=Path, help="default: data/raw/replay/<case>.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.mock:
            case, out = build_mock_case(), args.out or MOCK_OUT
        else:
            case = export_session(args.session, args.dir)
            out = args.out or DEFAULT_OUT_DIR / f"case-{args.session[:8]}.json"
        write_case(case, out)
    except ReplayError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    counts = Counter(step["status"] for step in case["steps"])
    print(f"Wrote {out}: {len(case['steps'])} steps, {len(case['context'])} context events.")
    print(f"Statuses: {dict(counts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
