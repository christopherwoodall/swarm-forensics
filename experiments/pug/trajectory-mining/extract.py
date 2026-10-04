"""Shape-based extraction of facts from raw dataset records.

All readers inspect the object shape. They never assume one provider schema.
Functions return sanitized, bounded text with a field path for every claim.
Diagnostics MUST NOT contain record values.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from contract import sanitize_text

MAX_DETAIL_CHARS = 400
MAX_OUTPUT_CHARS = 300
MAX_NARRATION_CHARS = 240
MAX_MESSAGE_CHARS = 1500
MAX_ARTIFACTS_PER_TEXT = 20

SHAPES = (
    "empty",
    "plain_text",
    "anthropic_blocks",
    "gemini_candidates",
    "openai_response_items",
    "chat_completions",
)

# Base classifier follows `swarm_forensics.replay._classify`.
DESKTOP_ACTIONS = frozenset(
    {
        "mouse_move", "left_click", "right_click", "middle_click", "double_click",
        "triple_click", "left_click_drag", "left_mouse_down", "left_mouse_up", "key", "type",
        "hold_key", "scroll", "screenshot", "cursor_position", "view_clipboard",
        "get_pixel_coords_of_element",
    }
)  # fmt: skip
REQUEST_ACTIONS = frozenset(
    {"request_human_helper", "request_Google_sign_in", "request_approval_for_unsolicited_outreach"}
)
TEXT_NOT_STORED = frozenset({"type", "key", "hold_key"})

_WORK_SIGNALS = (
    ("git-push", re.compile(r"\bgit\s+push\b")),
    ("http", re.compile(r"\b(?:curl|wget)\b|requests\.(?:get|post|put|delete)\s*\(")),
    ("file-write", re.compile(r"write_text\s*\(|\.write\s*\(|\bcat\s+[^\n]*>|<<\s*['\"]?\w+")),
    ("python", re.compile(r"\bpython[0-9.]*\b")),
)

_URL = re.compile(r"https?://[^\s<>'\"\\)\]}]+", re.IGNORECASE)
_GDOC = re.compile(
    r"docs\.google\.com/(document|spreadsheets|presentation|forms)/d/([A-Za-z0-9_-]{15,})"
)
_REPO = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_-][A-Za-z0-9_.-]*)")
_FILE = re.compile(
    r"(?<![\w:/.~-])((?:/(?:home|workspace|tmp|root|mnt|opt|var/tmp)|~)/[\w@%+=,.\-/]{2,160})"
)
_HOST = re.compile(r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z][a-z0-9-]*")
_TRAILING = ".,;:!?)]}'\"`"
_NOT_REPO_OWNERS = frozenset({"settings", "login", "orgs", "topics", "features", "sponsors"})

ArtifactKind = str  # url, host, repo, file, document, title


@dataclass
class TurnFacts:
    action: str
    surface: str
    work: str
    detail: str
    detail_path: str
    output: str
    narration: str
    shape: str
    has_error: bool
    artifact_texts: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class MessageFacts:
    role: str
    text: str
    text_path: str
    shape: str
    tools: list[str]
    artifact_texts: list[tuple[str, str]] = field(default_factory=list)
    titles: list[str] = field(default_factory=list)


def shape_signature(value: Any) -> str:
    """Describe an unsupported shape by type and key names only. Values are never included."""
    if isinstance(value, dict):
        return "dict:" + ",".join(sorted(str(k)[:24] for k in value)[:8])
    if isinstance(value, list):
        inner = sorted({type(v).__name__ for v in value[:5]})
        return "list:" + ",".join(inner)
    return type(value).__name__


def classify_action(action: dict[str, Any]) -> tuple[str, str, str]:
    """Return (action name, surface, base work) for one recorded action."""
    if "command" in action:
        return "shell_command", "shell", "shell"
    name = str(action.get("action") or "")
    if not name:
        return "none", "other", "other"
    if name in DESKTOP_ACTIONS:
        return name, "desktop", "desktop"
    if name in ("pause", "wait"):
        return name, "idle", "idle"
    if name in ("send_message_back_to_chat", "move_to_room"):
        return name, "chat", "chat"
    if name == "search_history":
        return name, "history", "search"
    if name in REQUEST_ACTIONS:
        return name, "request", "request"
    return name, "other", "other"


def _block_texts(blocks: list[Any], path: str, include_tools: bool) -> tuple[list[tuple[str, str]], list[str]]:
    texts: list[tuple[str, str]] = []
    tools: list[str] = []
    for i, block in enumerate(blocks):
        if isinstance(block, str):
            texts.append((f"{path}[{i}]", block))
            continue
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        bpath = f"{path}[{i}]"
        if kind in ("text", "output_text", "summary_text") and isinstance(block.get("text"), str):
            texts.append((f"{bpath}.text", block["text"]))
        elif kind == "tool_use":
            name = str(block.get("name") or "tool")[:80]
            tools.append(name)
            if include_tools:
                texts.append((f"{bpath}.input", f"[{name}] {_tool_input_summary(block.get('input'))}"))
        elif kind == "tool_result" and include_tools:
            inner = block.get("content")
            if isinstance(inner, str):
                texts.append((f"{bpath}.content", inner))
            elif isinstance(inner, list):
                sub, _ = _block_texts(inner, f"{bpath}.content", False)
                texts.extend(sub)
    return texts, tools


def _tool_input_summary(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    keys = ("command", "url", "file_path", "path", "query", "title", "content", "text", "description")
    parts = []
    for key in keys:
        item = value.get(key)
        if isinstance(item, str) and item:
            parts.append(f"{key}={item[:300]}")
    return " ".join(parts)


def read_payload(payload: Any, path: str, include_tools: bool = False) -> tuple[str, list[tuple[str, str]], list[str]]:
    """Read text by shape. Return (shape name, [(field_path, text)], tool names)."""
    if payload is None or payload == "" or payload == [] or payload == {}:
        return "empty", [], []
    if isinstance(payload, str):
        return "plain_text", [(path, payload)], []
    if isinstance(payload, list):
        if all(isinstance(i, dict) and "type" in i for i in payload) and payload:
            items: list[tuple[str, str]] = []
            tools: list[str] = []
            for i, item in enumerate(payload):
                ipath = f"{path}[{i}]"
                kind = item.get("type")
                if kind == "message" and isinstance(item.get("content"), list):
                    sub, _ = _block_texts(item["content"], f"{ipath}.content", False)
                    items.extend(sub)
                elif kind == "reasoning" and isinstance(item.get("summary"), list):
                    sub, _ = _block_texts(item["summary"], f"{ipath}.summary", False)
                    items.extend(sub)
                elif kind in ("function_call", "custom_tool_call"):
                    tools.append(str(item.get("name") or "tool")[:80])
                    if include_tools and isinstance(item.get("arguments"), str):
                        items.append((f"{ipath}.arguments", item["arguments"]))
                elif kind in ("text", "output_text", "tool_use", "tool_result"):
                    sub, t = _block_texts([item], path, include_tools)
                    items.extend(sub)
                    tools.extend(t)
            shape = "anthropic_blocks" if any(i.get("type") in ("text", "tool_use", "tool_result") for i in payload) else "openai_response_items"
            return shape, items, tools
        return "unsupported", [], []
    if isinstance(payload, dict):
        if isinstance(payload.get("candidates"), list):
            texts = []
            tools = []
            for ci, cand in enumerate(payload["candidates"]):
                content = cand.get("content") if isinstance(cand, dict) else None
                parts = content.get("parts") if isinstance(content, dict) else None
                for pi, part in enumerate(parts if isinstance(parts, list) else []):
                    if not isinstance(part, dict):
                        continue
                    ppath = f"{path}.candidates[{ci}].content.parts[{pi}]"
                    if isinstance(part.get("text"), str):
                        texts.append((f"{ppath}.text", part["text"]))
                    call = part.get("functionCall")
                    if isinstance(call, dict):
                        tools.append(str(call.get("name") or "tool")[:80])
            return "gemini_candidates", texts, tools
        if isinstance(payload.get("choices"), list):
            texts = []
            tools = []
            for ci, choice in enumerate(payload["choices"]):
                msg = choice.get("message") if isinstance(choice, dict) else None
                if not isinstance(msg, dict):
                    continue
                if isinstance(msg.get("content"), str) and msg["content"]:
                    texts.append((f"{path}.choices[{ci}].message.content", msg["content"]))
                for call in msg.get("tool_calls") or []:
                    fn = call.get("function") if isinstance(call, dict) else None
                    if isinstance(fn, dict):
                        tools.append(str(fn.get("name") or "tool")[:80])
            return "chat_completions", texts, tools
        content = payload.get("content")
        if isinstance(content, list):
            texts, tools = _block_texts(content, f"{path}.content", include_tools)
            return "anthropic_blocks", texts, tools
        if isinstance(content, str):
            return "plain_text", [(f"{path}.content", content)], []
        if isinstance(payload.get("message"), dict):
            return read_payload(payload["message"], f"{path}.message", include_tools)
        if isinstance(payload.get("text"), str):
            return "plain_text", [(f"{path}.text", payload["text"])], []
    return "unsupported", [], []


def extract_turn(record: dict[str, Any]) -> TurnFacts:
    """Read one `computer_use_turns` record."""
    raw = record.get("agent_action")
    action = raw if isinstance(raw, dict) else {}
    name, surface, work = classify_action(action)
    command = action.get("command") if isinstance(action.get("command"), str) else ""
    if surface == "shell":
        for label, pattern in _WORK_SIGNALS:
            if pattern.search(command):
                work = label
                break

    detail, detail_path = "", ""
    artifact_texts: list[tuple[str, str]] = []
    if command:
        detail, detail_path = command, "agent_action.command"
    elif name == "send_message_back_to_chat" and isinstance(action.get("content"), str):
        detail, detail_path = action["content"], "agent_action.content"
    elif name == "search_history" and isinstance(action.get("query"), str):
        detail, detail_path = action["query"], "agent_action.query"
    elif isinstance(action.get("description"), str):
        detail, detail_path = action["description"], "agent_action.description"
    elif name in ("move_to_room",) and isinstance(action.get("roomName"), str):
        detail, detail_path = action["roomName"], "agent_action.roomName"
    if name in TEXT_NOT_STORED:
        typed = action.get("text")
        if isinstance(typed, str):
            artifact_texts.append(("agent_action.text", typed))
    elif isinstance(action.get("text"), str) and not detail:
        detail, detail_path = action["text"], "agent_action.text"
    if detail:
        artifact_texts.append((detail_path, detail))

    output = turn_text(record.get("output"))
    error = turn_text(record.get("error"))
    if output:
        artifact_texts.append(("output", output))
    if error:
        artifact_texts.append(("error", error))

    shape, texts, _ = read_payload(record.get("agent_messages"), "agent_messages")
    narration = " ".join(t for _, t in texts if t)[:MAX_NARRATION_CHARS * 3]
    return TurnFacts(
        action=name,
        surface=surface,
        work=work,
        detail=sanitize_text(detail, MAX_DETAIL_CHARS),
        detail_path=detail_path,
        output=sanitize_text(output or error, MAX_OUTPUT_CHARS),
        narration=sanitize_text(narration, MAX_NARRATION_CHARS),
        shape=shape,
        has_error=bool(error),
        artifact_texts=artifact_texts,
    )


def turn_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False)[:2000]
        except (TypeError, ValueError):
            return ""
    return ""


def extract_cc_message(record: dict[str, Any]) -> MessageFacts:
    """Read one `claude_code_messages` record. The payload sits in `content`."""
    role = str(record.get("message_type") or "unknown")
    content = record.get("content")
    shape, texts, tools = read_payload(content, "content", include_tools=True)
    if shape == "unsupported" and isinstance(content, dict):
        inner = content.get("message")
        for holder, prefix in ((content, "content"), (inner, "content.message")):
            if not isinstance(holder, dict):
                continue
            for key in ("result", "summary"):
                if isinstance(holder.get(key), str) and holder[key]:
                    shape, texts = "plain_text", [(f"{prefix}.{key}", holder[key])]
                    break
            if shape != "unsupported":
                break
    joined = "\n".join(t for _, t in texts)
    titles = tool_titles(content)
    first_path = texts[0][0] if texts else "content"
    return MessageFacts(
        role=role,
        text=sanitize_text(joined, MAX_MESSAGE_CHARS),
        text_path=first_path,
        shape=shape,
        tools=tools,
        artifact_texts=list(texts),
        titles=titles,
    )


def tool_titles(content: Any) -> list[str]:
    """Return document titles named in tool call inputs (`title` field)."""
    message = content.get("message") if isinstance(content, dict) else None
    blocks = message.get("content") if isinstance(message, dict) else None
    out: list[str] = []
    for block in blocks if isinstance(blocks, list) else []:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            inp = block.get("input")
            title = inp.get("title") if isinstance(inp, dict) else None
            if isinstance(title, str) and 3 <= len(title.strip()) <= 120:
                out.append(sanitize_text(title.strip(), 120))
    return out[:5]


def clean_url(raw: str) -> str:
    return raw.rstrip(_TRAILING)


def extract_artifacts(
    text: str, agent_id: str | None = None, limit: int = MAX_ARTIFACTS_PER_TEXT
) -> list[tuple[str, str, str]]:
    """Return (kind, identifier, scope) tuples found in `text`.

    URL, host, repo, and document identifiers use scope `global`.
    File paths use scope `agent:<id>`. Equal paths on two agents MUST NOT merge.
    """
    found: dict[tuple[str, str, str], None] = {}

    def add(kind: str, ident: str, scope: str = "global") -> None:
        if len(found) < limit and ident:
            found.setdefault((kind, ident, scope))

    for raw in _URL.findall(text):
        url = clean_url(raw)
        body = url.split("://", 1)[1]
        host = body.split("/", 1)[0].rsplit("@", 1)[-1].split(":")[0].lower().rstrip(".")
        if not _HOST.fullmatch(host):
            continue
        add("host", host)
        path = body.split("/", 1)[1] if "/" in body else ""
        path = re.split(r"[?#]", path, maxsplit=1)[0]
        add("url", f"{host}/{path}".rstrip("/")[:200])
    for kind, doc_id in _GDOC.findall(text):
        add("document", f"gdoc:{kind}:{doc_id}")
    for owner, repo in _REPO.findall(text):
        if owner.lower() in _NOT_REPO_OWNERS:
            continue
        add("repo", f"{owner}/{repo.removesuffix('.git')}".lower().rstrip(_TRAILING))
    for path in _FILE.findall(text):
        path = path.rstrip(_TRAILING)
        if agent_id and len(path) > 4:
            add("file", path, f"agent:{agent_id}")
    return list(found)
