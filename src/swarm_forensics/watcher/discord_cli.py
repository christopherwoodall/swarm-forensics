"""Machine-readable, read-only Discord channel collector CLI."""

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

from .discord_source import Archive, DiscordReader, SourceError, poll

DEFAULT_DB = (Path(__file__).resolve().parents[3] / "data/raw/discord"
              / "1430962817045106792/source.sqlite")


def main(argv=None, *, token=None, fetch=None, now=time.time):
    """Run commands; accept an in-process token without an argv credential."""
    parser = argparse.ArgumentParser(description="Read-only Discord channel source archive")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("poll", "pending", "ack", "status", "monitor"):
        command = commands.add_parser(name)
        if name in ("poll", "monitor"):
            command.add_argument("--max-pages", type=int, default=20)
            command.add_argument("--total-seconds", type=float, default=30)
        if name == "monitor":
            command.add_argument("--retry-seconds", type=float, default=900)
        if name == "pending":
            command.add_argument("--limit", type=int, default=50)
        if name == "ack":
            command.add_argument("--cursor", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        with Archive(args.db) as archive:
            if args.command in ("poll", "monitor"):
                def poll_once():
                    selected = fetch
                    if selected is None:
                        # Cron SHOULD inject only this scoped credential in process.
                        credential = token if token is not None else os.environ.get(
                            "DISCORD_BOT_TOKEN")
                        selected = DiscordReader(credential).fetch
                    return poll(archive, selected, max_pages=args.max_pages,
                                total_seconds=args.total_seconds, now=now)

                if args.command == "poll":
                    value = poll_once()
                else:
                    failure = None
                    try:
                        poll_once()
                    except SourceError as error:
                        failure = error
                    value = archive.change_token(now=now(), retry_seconds=args.retry_seconds)
                    print(value)
                    if failure is not None:
                        print(f"Discord monitor: {failure}", file=sys.stderr)
                        return 1
                    return 0
            elif args.command == "pending":
                value = archive.pending(args.limit)
            elif args.command == "ack":
                value = archive.ack(args.cursor)
            else:
                value = archive.status()
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
        return 0
    except SourceError as error:
        print(f"Discord collector: {error}", file=sys.stderr)
    except (sqlite3.DatabaseError, OSError):
        print("Discord collector: archive failure", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
