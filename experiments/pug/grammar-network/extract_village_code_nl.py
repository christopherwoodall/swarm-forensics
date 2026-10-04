#!/usr/bin/env python3
"""Extract natural-language text from village code-adjacent messages.

Sources (read-only):
  claude_code_messages.jsonl.gz -- nested content dicts (tool results,
      file-creation notices, code blocks)
  computer_use_turns.jsonl.gz  -- agent_messages text, command comments
      ('# ...' lines inside shell commands are agent voice)
Output: data/processed/village_code_nl.jsonl, one record per message/turn:
  {"src": "claude"|"turns", "id": ..., "text": "..."}
Code-fence contents are kept: code-adjacent NL is the point.
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_RAW = HERE.parent / "stylometry" / "data" / "raw"
OUT = HERE / "data" / "processed" / "village_code_nl.jsonl"


def walk(x, out):
    if isinstance(x, str):
        s = x.strip()
        if len(s) > 2:
            out.append(s)
    elif isinstance(x, dict):
        for v in x.values():
            walk(v, out)
    elif isinstance(x, list):
        for v in x:
            walk(v, out)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(OUT, "w", encoding="utf-8") as out:
        p = DATA_RAW / "claude_code_messages.jsonl.gz"
        if p.exists():
            with gzip.open(p, "rt", encoding="utf-8") as f:
                for line in f:
                    r = json.loads(line)
                    texts = []
                    walk(r.get("content"), texts)
                    t = "\n".join(texts)
                    if t.strip():
                        out.write(json.dumps({"src": "claude",
                                              "id": r.get("id"), "text": t[:8000]}) + "\n")
                        n += 1
        p = DATA_RAW / "computer_use_turns.jsonl.gz"
        if p.exists():
            try:
                with gzip.open(p, "rt", encoding="utf-8") as f:
                    for line in f:
                        r = json.loads(line)
                        texts = []
                        walk(r.get("agent_messages"), texts)
                        a = r.get("agent_action")
                        if isinstance(a, dict) and isinstance(a.get("command"), str):
                            for ln in a["command"].splitlines():
                                s = ln.strip()
                                if s.startswith("#") and len(s) > 4:
                                    texts.append(s)
                        t = "\n".join(texts)
                        if t.strip():
                            out.write(json.dumps({"src": "turns",
                                                  "id": r.get("id"), "text": t[:8000]}) + "\n")
                            n += 1
            except EOFError:
                print("WARN truncated turns gzip tolerated", flush=True)
    print(f"village code-NL docs={n} -> {OUT}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
