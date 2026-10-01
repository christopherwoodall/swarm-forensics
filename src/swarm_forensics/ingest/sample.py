"""Write small synthetic tables that follow the AI Village schema.

Usage: python -m swarm_forensics.ingest.sample [--dest data/raw/sample] [--rows 50]

The command needs no network access and no credentials.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_DEST = Path("data/raw/sample")
START = datetime(2025, 4, 2, 17, 0, 0, tzinfo=timezone.utc)
ACTION_TYPES = ("AGENT_TALK", "START_USING_COMPUTER", "STOP_USING_COMPUTER", "WAIT", "USER_TALK")
AGENT_NAMES = ("Agent Alpha", "Agent Beta", "Agent Gamma")


def _id(kind: str, number: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"swarm-forensics/sample/{kind}/{number}"))


def _stamp(number: int) -> str:
    return (START + timedelta(minutes=number)).strftime("%Y-%m-%d %H:%M:%S.000000")


def _write(path: Path, rows: list[dict]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def build_tables(rows: int) -> dict[str, list[dict]]:
    """Return deterministic synthetic rows for `agent_goals`, `chat_messages`, and `events`."""
    room_id = _id("room", 0)
    agent_ids = [_id("agent", n) for n in range(len(AGENT_NAMES))]
    goals = [
        {
            "id": _id("agent_goal", n),
            "agent_id": agent_id,
            "name": f"Synthetic goal {n}",
            "short_name": f"goal-{n}",
            "description": f"Synthetic goal for {AGENT_NAMES[n]}.",
            "start_time": None,
            "end_time": None,
        }
        for n, agent_id in enumerate(agent_ids)
    ]
    messages = []
    events = []
    for n in range(rows):
        agent_index = n % len(agent_ids)
        action = ACTION_TYPES[n % len(ACTION_TYPES)]
        data = {"actionType": action}
        if action == "AGENT_TALK":
            data["speakerId"] = agent_ids[agent_index]
        elif action == "USER_TALK":
            data["speakerName"] = "Synthetic viewer"
        else:
            data["agentId"] = agent_ids[agent_index]
        if action in ("AGENT_TALK", "USER_TALK"):
            message_id = _id("message", n)
            content = f"Synthetic message {n}."
            messages.append(
                {
                    "id": message_id,
                    "speaker_type": "user" if action == "USER_TALK" else "agent",
                    "agent_speaker_id": None if action == "USER_TALK" else agent_ids[agent_index],
                    "user_speaker_id": None,
                    "content": content,
                    "room_id": room_id,
                    "has_been_approved": None,
                    "created_at": _stamp(n),
                    "updated_at": _stamp(n),
                }
            )
            data.update({"messageId": message_id, "roomId": room_id, "content": content})
        events.append(
            {
                "id": _id("event", n),
                "event_index": n,
                "data": data,
                "created_at": _stamp(n),
                "updated_at": _stamp(n),
            }
        )
    return {"agent_goals": goals, "chat_messages": messages, "events": events}


def write_sample(dest: Path, rows: int) -> list[Path]:
    """Write the synthetic tables to `dest` and return the file paths."""
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, table in build_tables(rows).items():
        path = dest / f"{name}.jsonl.gz"
        _write(path, table)
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="default: data/raw/sample")
    parser.add_argument("--rows", type=int, default=50, help="event rows to generate")
    args = parser.parse_args(argv)
    for path in write_sample(args.dest, args.rows):
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
