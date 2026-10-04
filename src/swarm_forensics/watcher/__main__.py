"""Run bounded source collection through Make targets."""

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

from .collector import SESSION, Archive, PeerReader, SourceError, poll

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB = ROOT / "data" / "raw" / "fairystack" / SESSION / "source.sqlite"
DEFAULT_CONFIG = Path.home() / ".config" / "fairystack-watcher" / f"{SESSION}.json"


def report_error(error):
    detail = str(error) if isinstance(error, SourceError) else type(error).__name__
    print(json.dumps({"error": detail}), file=sys.stderr)


def main(argv=None, *, fetch=None, now=time.time):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    pending = commands.add_parser("pending")
    pending.add_argument("--limit", type=int, default=50)
    ack = commands.add_parser("ack")
    ack.add_argument("--cursor", type=int, required=True)
    for command in ("poll", "monitor"):
        acquire = commands.add_parser(command)
        acquire.add_argument("--max-pages", type=int, default=20)
        acquire.add_argument("--total-seconds", type=float, default=30)
        if command == "monitor":
            acquire.add_argument("--retry-seconds", type=float, default=900)
    args = parser.parse_args(argv)
    try:
        with Archive(args.db) as archive:
            if args.command == "status":
                result = archive.status()
            elif args.command == "pending":
                result = archive.pending(args.limit)
            elif args.command == "ack":
                result = archive.ack(args.cursor)
            else:
                code = 0
                try:
                    if fetch is None:
                        config = json.loads(args.config.read_text())
                        fetch = PeerReader(config).fetch
                    result = poll(archive, fetch, max_pages=args.max_pages,
                                  total_seconds=args.total_seconds, now=now)
                except (SourceError, OSError, ValueError, sqlite3.Error) as error:
                    if args.command != "monitor":
                        raise
                    report_error(error)
                    code = 1
                if args.command == "monitor":
                    print(archive.change_token(now=now(), retry_seconds=args.retry_seconds))
                    return code
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (SourceError, OSError, ValueError, sqlite3.Error) as error:
        report_error(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
