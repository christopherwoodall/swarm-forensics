"""Synthetic fixtures shaped like the real export. Offline. No dataset text.

Field names follow the real records: `agent_action`, `agent_messages`, `sdk_session_id`,
`message_type`, `content`, `agent_speaker_id`, `data.actionType`, and so on.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

VILLAGE = "village-1"
A1, A2, A3 = "agent-1", "agent-2", "agent-3"
SECRET = "sk-1234567890abcdefXYZ"
EMAIL = "someone@example.com"


def write_gz_jsonl(path: Path, rows: list[dict], raw_lines: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
        for line in raw_lines or []:
            handle.write(line + "\n")


def _turn(tid: str, sid: str | None, when: str, action: dict | None, messages, **extra) -> dict:
    row = {
        "id": tid, "session_id": sid, "agent_action": action, "agent_messages": messages,
        "output": None, "error": None, "system": None, "screenshot_is_redacted": False,
        "has_redaction_been_overruled": False, "created_at": when, "updated_at": when,
    }  # fmt: skip
    row.update(extra)
    return row


GEMINI = {"candidates": [{"index": 0, "content": {"role": "model", "parts": [
    {"text": "I will clone the repo."},
    {"functionCall": {"id": "x", "args": {}, "name": "use_computer"}}]}}]}
OPENAI_ITEMS = [
    {"id": "rs_1", "type": "reasoning", "summary": [{"type": "summary_text", "text": "Check API."}]},
    {"id": "fc_1", "type": "function_call", "name": "use_computer", "call_id": "c1",
     "arguments": "{\"action\":\"x\"}"},
]  # fmt: skip
ANTHROPIC = {"id": "msg_1", "role": "assistant", "type": "message", "model": "claude-x",
             "content": [{"type": "text", "text": "Opening the doc."},
                         {"type": "tool_use", "id": "t", "name": "computer", "input": {}}]}  # fmt: skip
CHAT_COMPLETIONS = {"choices": [{"message": {"role": "assistant", "content": "Done writing."}}]}
UNSUPPORTED = {"weird": 1, "shape": ["x"]}


def generate_synthetic_dataset(base: Path, big_turns: int = 0) -> dict[str, int]:
    """Write all tables. Return the row counts written to the manifest.

    `big_turns` adds session `s-big` (agent-3) with that many turns, to test aggregation.
    """
    base.mkdir(parents=True, exist_ok=True)
    agents = [
        {"id": A1, "name": "Alpha", "model_string": "z-ai/glm-5.3-flash"},
        {"id": A2, "name": "Beta", "model_string": "claude-opus"},
        {"id": A3, "name": "Gamma", "model_string": "gpt-x"},
    ]
    rooms = [{"id": "room-a", "name": "general"}, {"id": "room-b", "name": "focus"}]
    village_goals = [
        {"id": "vg-1", "village_id": VILLAGE, "goal": "Build infrastructure\nand more",
         "start_time": "2026-04-20 00:00:00", "end_time": "2026-04-25 00:00:00"},
        {"id": "vg-2", "village_id": VILLAGE, "goal": "Investigate security",
         "start_time": "2026-04-24 00:00:00.5", "end_time": "2026-05-01 00:00:00"},
    ]  # fmt: skip
    agent_goals = [
        {"id": "ag-1", "agent_id": A1, "name": "Verify routing", "short_name": "Routing",
         "description": None, "start_time": "2026-04-21 10:00:00", "end_time": None},
    ]  # fmt: skip
    sessions = [
        {"id": "s1", "agent_id": A1, "created_at": "2026-04-21 12:00:00.123456",
         "updated_at": "2026-04-21 12:00:00.123457",
         "session_goal": "Clone repo and run the \"lantern protocol\" checks",
         "short_displayed_session_goal": "Clone and check"},
        {"id": "s2", "agent_id": A2, "created_at": "2026-04-22 08:00:00",
         "updated_at": "2026-04-22 08:00:00", "session_goal": None,
         "short_displayed_session_goal": None},
        {"id": "s3", "agent_id": A1, "created_at": "2026-04-24 23:00:00",
         "updated_at": "2026-04-24 23:00:00", "session_goal": "Bridge the boundary",
         "short_displayed_session_goal": "Bridge"},
        {"id": "s4", "agent_id": A2, "created_at": "2026-06-01 00:00:00",
         "updated_at": "2026-06-01 00:00:00", "session_goal": "   ",
         "short_displayed_session_goal": None},
        {"id": "s-empty", "agent_id": A3, "created_at": "2026-04-22 09:00:00",
         "updated_at": "2026-04-22 09:00:00", "session_goal": "No turns recorded",
         "short_displayed_session_goal": None},
        {"id": "s-ghost", "agent_id": "agent-ghost", "created_at": "2026-04-22 10:00:00",
         "updated_at": "2026-04-22 10:00:00", "session_goal": "Agent row is missing",
         "short_displayed_session_goal": None},
    ]  # fmt: skip
    turns = [
        _turn("t1", "s1", "2026-04-21 12:01:00.5",
              {"command": "git clone https://github.com/pug/core.git /home/computeruse/work/notes.txt"},
              GEMINI, output=f"Cloning...\nAuthorization: Bearer {SECRET}\ncontact {EMAIL}"),
        _turn("t2", "s1", "2026-04-21 12:02:00",
              {"command": "curl https://api.target-host.org/v1/items?token=abc"}, OPENAI_ITEMS,
              output="ok", error="warning"),
        _turn("t3", "s1", "2026-04-21 12:30:00",
              {"action": "send_message_back_to_chat",
               "content": "We follow the \"lantern protocol\" for xylophonic checks"}, None),
        _turn("t4", "s3", "2026-04-24 23:05:00",
              {"action": "left_click", "coordinate": [1, 2], "text": None}, ANTHROPIC,
              output=json.dumps({"url": "https://docs.google.com/document/d/1AbCdEfGhIjKlMnOpQrSt/edit"})),
        _turn("t5", "s3", "2026-04-25 02:00:00", {"command": "ls /home/computeruse/work/notes.txt"},
              CHAT_COMPLETIONS, output="notes.txt"),
        _turn("t6", "s2", "2026-04-22 08:05:00",
              {"action": "type", "text": "https://example.org/typed/page"}, UNSUPPORTED,
              output="/home/computeruse/work/notes.txt"),
        _turn("t7", "s-missing", "2026-04-22 08:06:00", {"action": "screenshot"}, None),
        _turn("t8", None, "2026-04-22 08:07:00", {"action": "screenshot"}, None),
    ]
    if big_turns:
        sessions.append({"id": "s-big", "agent_id": A3, "created_at": "2026-04-23 00:00:00",
                         "updated_at": "2026-04-23 00:00:00", "session_goal": "Large trace",
                         "short_displayed_session_goal": "Large"})  # fmt: skip
        for i in range(big_turns):
            when = f"2026-04-23 00:{i // 60:02d}:{i % 60:02d}"
            action = {"command": f"echo {i}"} if i % 3 == 0 else {"action": "screenshot"}
            turns.append(_turn(f"b{i:04d}", "s-big", when, action, None))
    cc_sessions = [
        {"id": "cc-1", "agent_id": A2, "sdk_session_id": "sdk-1",
         "created_at": "2026-04-21 13:00:00", "updated_at": "2026-04-21 13:00:00"},
    ]  # fmt: skip

    def cc(mid: str, sdk: str, kind: str, when: str, inner: dict) -> dict:
        return {"id": mid, "agent_id": A2, "sdk_session_id": sdk, "message_uuid": None,
                "message_type": kind, "message_subtype": None, "created_at": when,
                "content": {"type": kind, "uuid": mid, "message": inner, "session_id": sdk,
                            "parent_tool_use_id": None}}  # fmt: skip

    cc_messages = [
        cc("m1", "sdk-1", "assistant", "2026-04-21 13:01:00", {
            "role": "assistant", "content": [
                {"type": "text", "text": "Saying \"lantern protocol\" again; see https://github.com/pug/core"},
                {"type": "tool_use", "id": "u1", "name": "mcp__docs__create",
                 "input": {"title": "Protocol notes", "content": "x"}}]}),
        cc("m2", "sdk-1", "user", "2026-04-21 13:02:00", {
            "role": "user", "content": [{"type": "tool_result", "tool_use_id": "u1",
                                         "content": [{"type": "text", "text": "created"}]}]}),
        cc("m3", "sdk-1", "system", "2026-04-21 13:03:00", {"subtype": "init", "result": "ready"}),
        cc("m4", "sdk-missing", "assistant", "2026-04-21 13:04:00",
           {"role": "assistant", "content": [{"type": "text", "text": "Orphan"}]}),
        cc("m5", "sdk-1", "assistant", "2026-04-21 13:05:00", {"weird": True}),
    ]

    def chat(cid: str, speaker: str | None, stype: str, when: str, text, room="room-a") -> dict:
        return {"id": cid, "agent_speaker_id": speaker if stype == "agent" else None,
                "user_speaker_id": None if stype == "agent" else speaker, "speaker_type": stype,
                "content": text, "room_id": room, "created_at": when, "updated_at": when,
                "has_been_approved": None}  # fmt: skip

    chat_messages = [
        chat("c1", A1, "agent", "2026-04-21 14:00:00", "Repo is at github.com/pug/core"),
        chat("c2", A2, "agent", "2026-04-21 14:01:00", "Yes, the \"lantern protocol\" works"),
        chat("c3", A1, "agent", "2026-04-21 14:02:00", "Thanks"),
        chat("c4", A2, "agent", "2026-04-21 16:00:00", "A second episode begins"),
        chat("c5", "human-1", "user", "2026-04-21 16:05:00", "Hello from a human"),
        chat("c6", A3, "agent", "2026-04-21 14:00:30", "Other room", room="room-b"),
    ]

    def event(eid: str, index: int, when: str, **data) -> dict:
        return {"id": eid, "event_index": index, "data": data, "village_id": VILLAGE,
                "created_at": when, "updated_at": when}  # fmt: skip

    events = [
        event("e1", 10, "2026-04-21 14:00:00", actionType="AGENT_TALK", messageId="c1",
              chatMessageId="c1", content="Repo is at github.com/pug/core", roomId="room-a",
              speakerId=A1, speakerType="agent"),
        event("e2", 11, "2026-04-21 14:00:00", actionType="AGENT_TALK", messageId="c-gone",
              content="Unmatched talk", roomId="room-a", speakerId=A1, speakerType="agent"),
        event("e3", 11, "2026-04-21 14:00:00", actionType="START_USING_COMPUTER",
              agentId=A1, computerUseSessionId="s1", sessionGoal="Clone repo",
              shortDisplayedSessionGoal="Clone"),
        event("e4", 12, "2026-04-21 14:10:00", actionType="STOP_USING_COMPUTER", summary="done"),
        event("e5", 13, "2026-04-21 14:11:00", actionType="PAUSE", seconds=30),
        event("e6", 14, "2026-04-21 14:12:00", actionType="USER_TALK", messageId="c5"),
    ]
    tables = {
        "agents": agents, "chat_rooms": rooms, "village_goals": village_goals,
        "agent_goals": agent_goals, "computer_use_sessions": sessions,
        "computer_use_turns": turns, "claude_code_sessions": cc_sessions,
        "claude_code_messages": cc_messages, "chat_messages": chat_messages, "events": events,
    }  # fmt: skip
    for name, rows in tables.items():
        write_gz_jsonl(base / f"{name}.jsonl.gz", rows)
    counts = {name: len(rows) for name, rows in tables.items()}
    (base / "manifest.json").write_text(
        json.dumps({"villageId": VILLAGE, "rowCounts": counts}), encoding="utf-8"
    )
    return counts
