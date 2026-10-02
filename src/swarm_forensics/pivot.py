"""Check the pivot graph file used by the v3_transluce viewer.

Usage:
    python -m swarm_forensics.pivot [--file PATH]

The file holds aggregate counts from another investigation. This module does not
rebuild the counts from the raw archives. It only checks the shape of the file, so the
viewer can trust it. Error messages MUST NOT contain record values.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, NoReturn

from swarm_forensics.replay import ReplayError

DEFAULT_FILE = Path("data/viz_mock/v3_transluce/data/graph.json")
LAYERS = ("source", "launcher", "pivot", "target")
PREFIX = {"source": "S:", "launcher": "L:", "pivot": "P:", "target": "T:"}
EDGE_LAYERS = (("source", "launcher"), ("launcher", "pivot"), ("pivot", "target"))
BADGES = (None, "new lead", "CONFIRMED", "CANDIDATE", "HYPOTHESIS", "HONEST GAP")
CONFIDENCE = ("confirmed", "candidate", "hypothesized")
META_KEYS = ("source", "day0", "day1", "ndays", "note", "nodes", "edges")


def _fail(path: str, reason: str) -> NoReturn:
    raise ReplayError("graph", reason, path)


def _need(obj: Any, path: str, keys: tuple[str, ...]) -> None:
    if not isinstance(obj, dict):
        _fail(path, "must be an object")
    for key in keys:
        if key not in obj:
            _fail(f"{path}.{key}", "required field is missing")


def _count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _day(value: Any, path: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        _fail(path, "must be a YYYY-MM-DD date")


def validate_graph(graph: Any) -> None:
    """Raise ReplayError when `graph` breaks the contract."""
    _need(graph, "$", ("meta", "nodes", "edges", "days"))
    meta = graph["meta"]
    _need(meta, "$.meta", META_KEYS)
    first, last = _day(meta["day0"], "$.meta.day0"), _day(meta["day1"], "$.meta.day1")
    if not _count(meta["ndays"]) or meta["ndays"] != (last - first).days + 1:
        _fail("$.meta.ndays", "must equal the number of days from day0 to day1")

    layer_of: dict[str, str] = {}
    nodes = graph["nodes"]
    if not isinstance(nodes, list) or not nodes:
        _fail("$.nodes", "must be a non-empty list")
    for index, node in enumerate(nodes):
        path = f"$.nodes[{index}]"
        _need(node, path, ("id", "layer", "label", "size", "note", "badge", "dim"))
        if node["layer"] not in LAYERS:
            _fail(f"{path}.layer", "unknown layer")
        if not isinstance(node["id"], str) or not node["id"].startswith(PREFIX[node["layer"]]):
            _fail(f"{path}.id", "id must start with the layer prefix")
        if node["id"] in layer_of:
            _fail(f"{path}.id", "duplicate node id")
        layer_of[node["id"]] = node["layer"]
        if not _count(node["size"]):
            _fail(f"{path}.size", "must be a non-negative integer")
        if node["badge"] not in BADGES:
            _fail(f"{path}.badge", "unknown badge")
        if (node["layer"] == "source") != (node["badge"] in BADGES[2:]):
            _fail(f"{path}.badge", "source nodes need a confidence badge and other layers must not have one")
        if not isinstance(node["dim"], bool):
            _fail(f"{path}.dim", "must be true or false")
        for key in ("label", "note"):
            if not isinstance(node[key], str):
                _fail(f"{path}.{key}", "must be text")
    if any(layer not in layer_of.values() for layer in LAYERS):
        _fail("$.nodes", "every layer needs at least one node")
    if meta["nodes"] != len(nodes):
        _fail("$.meta.nodes", "must equal the number of nodes")

    edges = graph["edges"]
    if not isinstance(edges, list) or not edges:
        _fail("$.edges", "must be a non-empty list")
    for index, edge in enumerate(edges):
        path = f"$.edges[{index}]"
        _need(edge, path, ("a", "b", "w", "label"))
        if edge["a"] not in layer_of or edge["b"] not in layer_of:
            _fail(path, "edge refers to an unknown node")
        if (layer_of[edge["a"]], layer_of[edge["b"]]) not in EDGE_LAYERS:
            _fail(path, "edge must run source to launcher, launcher to pivot, or pivot to target")
        if (layer_of[edge["a"]] == "source") != ("conf" in edge):
            _fail(f"{path}.conf", "only source edges carry a confidence")
        if "conf" in edge and edge["conf"] not in CONFIDENCE:
            _fail(f"{path}.conf", "unknown confidence")
        if not _count(edge["w"]) or edge["w"] == 0:
            _fail(f"{path}.w", "must be a positive integer")
        if not isinstance(edge["label"], str):
            _fail(f"{path}.label", "must be text")
    if meta["edges"] != len(edges):
        _fail("$.meta.edges", "must equal the number of edges")

    days = graph["days"]
    if not isinstance(days, list) or len(days) != meta["ndays"]:
        _fail("$.days", "length must equal meta.ndays")
    for index, day in enumerate(days):
        path = f"$.days[{index}]"
        _need(day, path, ("d", "n", "digest"))
        if _day(day["d"], f"{path}.d") != first + timedelta(days=index):
            _fail(f"{path}.d", "days must be consecutive from day0")
        if not isinstance(day["n"], dict):
            _fail(f"{path}.n", "must be an object")
        for node_id, value in day["n"].items():
            if node_id not in layer_of:
                _fail(f"{path}.n", "refers to an unknown node")
            if not _count(value):
                _fail(f"{path}.n", "counts must be non-negative integers")
        digest = day["digest"]
        if not isinstance(digest, list) or not all(isinstance(line, str) for line in digest):
            _fail(f"{path}.digest", "must be a list of text lines")


def load_graph(path: Path) -> dict[str, Any]:
    """Read and check one graph file."""
    try:
        with path.open(encoding="utf-8") as handle:
            graph = json.load(handle)
    except FileNotFoundError:
        raise ReplayError("graph", "file not found") from None
    except (OSError, UnicodeDecodeError):
        raise ReplayError("graph", "unreadable file") from None
    except ValueError:
        raise ReplayError("graph", "malformed JSON") from None
    validate_graph(graph)
    return graph


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help=f"default: {DEFAULT_FILE}")
    args = parser.parse_args(argv)
    try:
        graph = load_graph(args.file)
    except ReplayError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"OK {args.file}: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges, {len(graph['days'])} days.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
