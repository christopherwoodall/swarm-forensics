"""Download the non-image files of the AI Village dataset.

Usage: python -m swarm_forensics.ingest.download {info,download} [options]

The command reads the access token from the HF_TOKEN environment variable.
The command MUST NOT print the token or any dataset content.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import HfHubHTTPError

REPO_ID = "aidigestorg/ai-village"
DEFAULT_DEST = Path("data/raw")

TABLES = (
    "agent_goals",
    "agent_memories",
    "agents",
    "chat_messages",
    "chat_rooms",
    "claude_code_messages",
    "claude_code_sessions",
    "computer_use_sessions",
    "computer_use_turns",
    "events",
    "summaries",
    "village_goals",
    "villages",
)

IMAGE_DIRECTORY = "images/"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".svg")
IGNORED_FILES = frozenset({".gitattributes"})


class DownloadError(Exception):
    """Raised for an expected failure. The message MUST NOT contain credentials."""


def is_image_path(path: str) -> bool:
    """Return True when the repository path is a screenshot or other image."""
    return path.startswith(IMAGE_DIRECTORY) or path.lower().endswith(IMAGE_SUFFIXES)


def parse_tables(names: list[str]) -> list[str]:
    """Return the table names. Raise DownloadError for an unknown name."""
    unknown = sorted(set(names) - set(TABLES))
    if unknown:
        raise DownloadError(
            f"Unknown table: {', '.join(unknown)}. Valid tables: {', '.join(TABLES)}."
        )
    return list(dict.fromkeys(names))


def select_files(files: dict[str, int], tables: list[str] | None = None) -> dict[str, int]:
    """Return the repository files to download, mapped to their size in bytes.

    Without `tables`, select every file that is not an image.
    With `tables`, select only the matching `<table>.jsonl.gz` files.
    """
    if tables is None:
        return {
            path: size
            for path, size in sorted(files.items())
            if not is_image_path(path) and path not in IGNORED_FILES
        }
    wanted = [f"{table}.jsonl.gz" for table in tables]
    missing = [path for path in wanted if path not in files]
    if missing:
        raise DownloadError(f"Table file not found in the dataset: {', '.join(missing)}.")
    return {path: files[path] for path in sorted(wanted)}


def pending_bytes(selected: dict[str, int], dest: Path) -> int:
    """Return the bytes still to transfer. Skip files that already have the full size."""
    total = 0
    for path, size in selected.items():
        local = dest / path
        if not (local.is_file() and local.stat().st_size == size):
            total += size
    return total


def free_bytes(dest: Path) -> int:
    """Return the free disk space for `dest`, using its nearest existing parent."""
    probe = dest.resolve()
    while not probe.exists():
        probe = probe.parent
    return shutil.disk_usage(probe).free


def check_disk_space(required: int, dest: Path) -> None:
    """Raise DownloadError when the disk cannot hold the pending transfer."""
    free = free_bytes(dest)
    if required > free:
        raise DownloadError(
            f"Not enough disk space: {format_size(required)} required, "
            f"{format_size(free)} free at {dest}."
        )


def format_size(size: float) -> str:
    """Return a human-readable size."""
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TiB"


def read_token() -> str:
    """Return the access token from the environment."""
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise DownloadError("HF_TOKEN is not set. Export a token that has dataset access.")
    return token


def describe_http_error(error: HfHubHTTPError) -> str:
    """Return a safe message for a Hub error, using the status code only."""
    status = getattr(getattr(error, "response", None), "status_code", None)
    if status in (401, 403):
        return (
            f"Access denied (HTTP {status}). Check HF_TOKEN and confirm that "
            f"access to {REPO_ID} was approved."
        )
    if status == 404:
        return "Not found (HTTP 404). Check the dataset name and the revision."
    return f"Hugging Face request failed (HTTP {status})."


def resolve_dataset(token: str, revision: str | None) -> tuple[str, dict[str, int]]:
    """Return the commit hash and the file sizes for one repository revision."""
    try:
        info = HfApi().dataset_info(
            REPO_ID, revision=revision, files_metadata=True, token=token
        )
    except HfHubHTTPError as error:
        raise DownloadError(describe_http_error(error)) from None
    files = {sibling.rfilename: sibling.size or 0 for sibling in info.siblings or []}
    return info.sha, files


def print_plan(sha: str, selected: dict[str, int], dest: Path) -> int:
    """Print the file list and sizes. Return the pending byte count."""
    print(f"Dataset: {REPO_ID}")
    print(f"Revision: {sha}")
    print(f"Destination: {dest}")
    for path, size in selected.items():
        print(f"  {format_size(size):>10}  {path}")
    pending = pending_bytes(selected, dest)
    print(f"Selected: {len(selected)} files, {format_size(sum(selected.values()))}")
    print(f"To transfer: {format_size(pending)}")
    print(f"Free disk space: {format_size(free_bytes(dest))}")
    return pending


def download_files(selected: dict[str, int], sha: str, dest: Path, token: str) -> None:
    """Download the selected files, pinned to one commit, directly into `dest`."""
    for path in selected:
        try:
            hf_hub_download(
                REPO_ID,
                path,
                repo_type="dataset",
                revision=sha,
                local_dir=dest,
                token=token,
            )
        except HfHubHTTPError as error:
            raise DownloadError(f"{path}: {describe_http_error(error)}") from None


def run(command: str, tables: list[str] | None, revision: str | None, dest: Path) -> None:
    """Run one command: `info` lists the plan, `download` also transfers the files."""
    names = parse_tables(tables) if tables else None
    token = read_token()
    sha, files = resolve_dataset(token, revision)
    selected = select_files(files, names)
    pending = print_plan(sha, selected, dest)
    if command == "info":
        return
    check_disk_space(pending, dest)
    dest.mkdir(parents=True, exist_ok=True)
    download_files(selected, sha, dest, token)
    print("Download complete.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("info", "download"))
    parser.add_argument("--tables", nargs="+", metavar="TABLE", help="download only these tables")
    parser.add_argument("--revision", help="commit hash, branch, or tag (default: main)")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="default: data/raw")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run(args.command, args.tables, args.revision, args.dest)
    except DownloadError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
