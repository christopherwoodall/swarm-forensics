#!/usr/bin/env python3
"""Drive the local SwarmChaser Discord bot.

Reads DISCORD_TOKEN from the environment or the repository .env file.
The token MUST stay out of command output and logs.

Usage:
  uv run python tools/discord_bot.py whoami
  uv run python tools/discord_bot.py guilds
  uv run python tools/discord_bot.py channels
  uv run python tools/discord_bot.py history --channel general --limit 20
  uv run python tools/discord_bot.py send --channel general --text "hello"
  uv run python tools/discord_bot.py online
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import Any

API = "https://discord.com/api/v10"
USER_AGENT = "SwarmChaserDriver (swarm-forensics, 0.1)"
TEXT_CHANNEL_TYPES = {0, 5}
JOIN_MESSAGE_TYPE = 7
ROOT = Path(__file__).resolve().parents[1]
MAX_MESSAGE_LENGTH = 2000


def configure_stdio() -> None:
    """Write UTF-8 to the console."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def load_token() -> str:
    """Return the bot token from the environment or .env."""
    token = os.environ.get("DISCORD_TOKEN", "").strip()
    if token:
        return token
    env_path = ROOT / ".env"
    if not env_path.is_file():
        raise SystemExit("Set DISCORD_TOKEN or create .env in the repository root.")
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "DISCORD_TOKEN":
            token = value.strip().strip('"').strip("'")
            break
    if not token:
        raise SystemExit("DISCORD_TOKEN is missing from .env.")
    return token


class DiscordError(Exception):
    """A Discord HTTP call failed."""


class DiscordClient:
    """Minimal Discord REST client for one bot token."""

    def __init__(self, token: str) -> None:
        self._token = token

    def request(self, method: str, path: str, payload: Mapping[str, Any] | None = None) -> Any:
        """Call the Discord API. Retry when Discord asks the client to wait."""
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        url = API + path
        for _attempt in range(6):
            request = urllib.request.Request(
                url,
                data=data,
                method=method,
                headers={
                    "Authorization": f"Bot {self._token}",
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request) as response:
                    body = response.read()
                    if not body:
                        return None
                    return json.loads(body)
            except urllib.error.HTTPError as err:
                detail = err.read().decode("utf-8", errors="replace")
                if err.code == 429:
                    time.sleep(_retry_after(detail) + 0.25)
                    continue
                raise DiscordError(f"HTTP {err.code}: {_public_error(detail)}") from err
        raise DiscordError("Discord rate limit persisted.")

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, payload: Mapping[str, Any]) -> Any:
        return self.request("POST", path, payload)


def _retry_after(detail: str) -> float:
    try:
        value = float(json.loads(detail).get("retry_after", 1))
    except (json.JSONDecodeError, TypeError, ValueError):
        return 1.0
    return value


def _public_error(detail: str) -> str:
    try:
        body = json.loads(detail)
    except json.JSONDecodeError:
        return "Discord rejected the request."
    message = body.get("message")
    if isinstance(message, str) and message:
        return message
    return "Discord rejected the request."


def _is_snowflake(value: str) -> bool:
    return value.isdigit() and len(value) >= 17


def guilds(client: DiscordClient) -> list[dict[str, Any]]:
    body = client.get("/users/@me/guilds")
    if not isinstance(body, list):
        raise DiscordError("Guild list had an unexpected shape.")
    return body


def resolve_guild(client: DiscordClient, name_or_id: str | None) -> dict[str, Any]:
    """Pick the only guild, or match a name or id."""
    found = guilds(client)
    if name_or_id is None:
        if len(found) == 1:
            return found[0]
        names = ", ".join(item.get("name", "?") for item in found) or "(none)"
        raise SystemExit(f"Pass --guild. The bot is in: {names}")
    for item in found:
        if item.get("id") == name_or_id or str(item.get("name", "")).casefold() == name_or_id.casefold():
            return item
    raise SystemExit(f"Guild not found: {name_or_id}")


def channel_rows(client: DiscordClient, guild_id: str) -> list[dict[str, Any]]:
    body = client.get(f"/guilds/{guild_id}/channels")
    if not isinstance(body, list):
        raise DiscordError("Channel list had an unexpected shape.")
    return body


def resolve_channel(
    client: DiscordClient,
    guild_id: str,
    name_or_id: str,
) -> dict[str, Any]:
    """Match a text channel by id or name."""
    rows = channel_rows(client, guild_id)
    if _is_snowflake(name_or_id):
        for row in rows:
            if row.get("id") == name_or_id:
                return row
        return {"id": name_or_id, "name": name_or_id, "type": 0}
    wanted = name_or_id.removeprefix("#").casefold()
    matches = [
        row
        for row in rows
        if str(row.get("name", "")).casefold() == wanted and row.get("type") in TEXT_CHANNEL_TYPES
    ]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"Text channel not found: {name_or_id}")
    raise SystemExit(f"Channel name is ambiguous: {name_or_id}")


def cmd_whoami(client: DiscordClient, _args: argparse.Namespace) -> None:
    me = client.get("/users/@me")
    print(f"{me.get('username')}  id={me.get('id')}  bot={me.get('bot')}")


def cmd_guilds(client: DiscordClient, _args: argparse.Namespace) -> None:
    found = guilds(client)
    if not found:
        print("The bot is not in any server.")
        return
    for item in found:
        print(f"{item.get('name')}  id={item.get('id')}")


def cmd_channels(client: DiscordClient, args: argparse.Namespace) -> None:
    guild = resolve_guild(client, args.guild)
    print(guild.get("name"))
    for row in channel_rows(client, guild["id"]):
        if row.get("type") not in TEXT_CHANNEL_TYPES:
            continue
        print(f"  #{row.get('name')}  id={row.get('id')}")


def cmd_history(client: DiscordClient, args: argparse.Namespace) -> None:
    guild = resolve_guild(client, args.guild)
    channel = resolve_channel(client, guild["id"], args.channel)
    remaining = args.limit
    before: str | None = args.before
    collected: list[dict[str, Any]] = []
    while remaining > 0:
        page_size = min(remaining, 100)
        path = f"/channels/{channel['id']}/messages?limit={page_size}"
        if before:
            path += f"&before={before}"
        page = client.get(path)
        if not isinstance(page, list) or not page:
            break
        collected.extend(page)
        remaining -= len(page)
        before = str(page[-1].get("id"))
        if len(page) < page_size:
            break
        time.sleep(0.4)
    for message in reversed(collected):
        _print_message(message)


def _print_message(message: Mapping[str, Any]) -> None:
    author = message.get("author") or {}
    name = author.get("global_name") or author.get("username") or "?"
    stamp = str(message.get("timestamp") or "")
    if message.get("type") == JOIN_MESSAGE_TYPE:
        print(f"[{stamp}] {name} joined")
        print()
        return
    print(f"[{stamp}] {name}")
    content = str(message.get("content") or "")
    if content:
        print(content)
    referenced = message.get("referenced_message") or {}
    if referenced:
        ref_author = referenced.get("author") or {}
        ref_name = ref_author.get("global_name") or ref_author.get("username") or "?"
        snippet = str(referenced.get("content") or "").replace("\n", " ")
        print(f"  reply to {ref_name}: {snippet[:160]}")
    print()


def cmd_send(client: DiscordClient, args: argparse.Namespace) -> None:
    text = args.text
    if not text.strip():
        raise SystemExit("Refusing to send an empty message.")
    if len(text) > MAX_MESSAGE_LENGTH:
        raise SystemExit(f"Message exceeds {MAX_MESSAGE_LENGTH} characters.")
    guild = resolve_guild(client, args.guild)
    channel = resolve_channel(client, guild["id"], args.channel)
    sent = client.post(f"/channels/{channel['id']}/messages", {"content": text})
    print(f"Sent to #{channel.get('name')}  id={sent.get('id')}")


def cmd_online(client: DiscordClient, _args: argparse.Namespace) -> None:
    """Hold a gateway session until the operator stops the process."""
    import base64
    import socket
    import ssl
    import struct

    info = client.get("/gateway/bot")
    url = str(info.get("url") or "wss://gateway.discord.gg")
    host = url.removeprefix("wss://").removeprefix("ws://").split("/", 1)[0]
    raw = socket.create_connection((host, 443), timeout=20)
    gateway = ssl.create_default_context().wrap_socket(raw, server_hostname=host)
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    handshake = (
        "GET /?v=10&encoding=json HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    gateway.sendall(handshake.encode("ascii"))
    prelude = b""
    while b"\r\n\r\n" not in prelude:
        chunk = gateway.recv(4096)
        if not chunk:
            raise DiscordError("Gateway closed during the handshake.")
        prelude += chunk
    status = prelude.split(b"\r\n", 1)[0].decode("ascii", errors="replace")
    if " 101 " not in status:
        raise DiscordError(f"Gateway handshake failed: {status}")

    def send_frame(opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack("!H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack("!Q", length)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        gateway.sendall(bytes(header) + mask + masked)

    def recv_exact(count: int) -> bytes:
        data = b""
        while len(data) < count:
            chunk = gateway.recv(count - len(data))
            if not chunk:
                raise DiscordError("Gateway closed.")
            data += chunk
        return data

    def recv_frame() -> tuple[int, bytes]:
        first, second = recv_exact(2)
        opcode = first & 0x0F
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", recv_exact(8))[0]
        return opcode, recv_exact(length)

    print("Connecting. Press Ctrl+C to disconnect.")
    identified = False
    heartbeat_seconds = 40.0
    next_heartbeat = time.monotonic() + heartbeat_seconds
    gateway.settimeout(5)
    try:
        while True:
            if time.monotonic() >= next_heartbeat:
                send_frame(1, json.dumps({"op": 1, "d": None}).encode("utf-8"))
                next_heartbeat = time.monotonic() + heartbeat_seconds
            try:
                opcode, payload = recv_frame()
            except TimeoutError:
                continue
            if opcode == 9:
                send_frame(10, payload)
                continue
            if opcode == 8:
                print("Gateway closed the session.")
                return
            if opcode != 1:
                continue
            event = json.loads(payload)
            if event.get("op") == 10 and not identified:
                interval_ms = (event.get("d") or {}).get("heartbeat_interval") or 41250
                heartbeat_seconds = max(float(interval_ms) / 1000.0, 1.0)
                next_heartbeat = time.monotonic() + heartbeat_seconds
                identify = {
                    "op": 2,
                    "d": {
                        "token": client._token,
                        "intents": 1,
                        "properties": {
                            "os": "windows",
                            "browser": "swarmchaser-driver",
                            "device": "swarmchaser-driver",
                        },
                    },
                }
                send_frame(1, json.dumps(identify).encode("utf-8"))
                identified = True
            elif event.get("op") == 0 and event.get("t") == "READY":
                user = (event.get("d") or {}).get("user") or {}
                print(f"Online as {user.get('username')}.")
    except KeyboardInterrupt:
        print("Disconnecting.")
    finally:
        try:
            send_frame(8, b"\x03\xe8")
        except OSError:
            pass
        gateway.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Drive the local SwarmChaser Discord bot.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("whoami", help="Print the bot user")
    sub.add_parser("guilds", help="List servers the bot has joined")

    channels = sub.add_parser("channels", help="List text channels in one server")
    channels.add_argument("--guild", help="Server name or id. Defaults to the only server.")

    history = sub.add_parser("history", help="Print recent messages, oldest first")
    history.add_argument("--channel", required=True, help="Channel name or id")
    history.add_argument("--guild", help="Server name or id. Defaults to the only server.")
    history.add_argument("--limit", type=int, default=20, help="Number of messages (default 20)")
    history.add_argument("--before", help="Return messages before this message id")

    send = sub.add_parser("send", help="Post one message")
    send.add_argument("--channel", required=True, help="Channel name or id")
    send.add_argument("--guild", help="Server name or id. Defaults to the only server.")
    send.add_argument("--text", required=True, help="Message text")

    sub.add_parser("online", help="Stay connected until Ctrl+C")
    return parser


def main(argv: list[str] | None = None) -> None:
    configure_stdio()
    args = build_parser().parse_args(argv)
    if getattr(args, "limit", 1) < 1:
        raise SystemExit("--limit must be at least 1.")
    client = DiscordClient(load_token())
    commands = {
        "whoami": cmd_whoami,
        "guilds": cmd_guilds,
        "channels": cmd_channels,
        "history": cmd_history,
        "send": cmd_send,
        "online": cmd_online,
    }
    try:
        commands[args.command](client, args)
    except DiscordError as err:
        raise SystemExit(str(err)) from err


if __name__ == "__main__":
    main()
