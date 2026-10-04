#!/usr/bin/env python3
"""Extract natural-language text embedded in the gem corpus source code.

Reads the 618 gem dirs at silent-locus/data/processed/gems/<name>-<ver>/ and
pulls: `#` line comments, `=begin`/`=end` blocks, double/single-quoted string
literals longer than 3 chars, and gemspec `description`/`summary` fields.
Output: data/processed/gems_code_nl.jsonl — one record per gem:
  {"gem": name, "comments": [...], "strings": [...], "text": "..."}
This is the `gems-code-nl` partition: agent-adjacent voice inside code.
Read-only on the gem corpus. Run: python3 extract_code_text.py
"""
import json
import re
import sys
from pathlib import Path

GEM_ROOT = Path("/home/hatch/workspace/silent-locus/data/processed/gems")
OUT_DIR = Path(__file__).resolve().parent / "data" / "processed"

LINE_COMMENT = re.compile(r"^\s*#(.*)$")
BLOCK_START = re.compile(r"^\s*=begin\b")
BLOCK_END = re.compile(r"^\s*=end\b")
DQUOTE = re.compile(r'"([^"\\]{4,})"')
SQUOTE = re.compile(r"'([^'\\]{4,})'")
GEMSPEC_FIELD = re.compile(r'\.\s*(description|summary)\s*=\s*["\'](.{4,}?)["\']')
CODE_EXTS = {".rb", ".gemspec", ".md", ".txt", ".rake", ".ru"}


def extract_file(path):
    comments, strings = [], []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return comments, strings
    in_block = False
    for line in text.splitlines():
        if BLOCK_START.match(line):
            in_block = True
            continue
        if BLOCK_END.match(line):
            in_block = False
            continue
        if in_block:
            s = line.strip()
            if len(s) > 3:
                comments.append(s)
            continue
        m = LINE_COMMENT.match(line)
        if m:
            s = m.group(1).strip()
            if len(s) > 3 and not s.startswith("!"):
                comments.append(s)
            continue
    for m in DQUOTE.finditer(text):
        strings.append(m.group(1).strip())
    for m in SQUOTE.finditer(text):
        strings.append(m.group(1).strip())
    for m in GEMSPEC_FIELD.finditer(text):
        strings.append(m.group(2).strip())
    return comments, strings


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "gems_code_nl.jsonl"
    if not GEM_ROOT.is_dir():
        # gems partition under audit; may be removed. Skip, don't crash.
        out_path.write_text("")
        print(f"SKIP gems source missing: {GEM_ROOT} (logged, not an error)")
        return
    n_gems = n_comments = n_strings = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for gem_dir in sorted(GEM_ROOT.iterdir()):
            if not gem_dir.is_dir():
                continue
            comments, strings = [], []
            for f in gem_dir.rglob("*"):
                if f.is_file() and f.suffix.lower() in CODE_EXTS:
                    c, s = extract_file(f)
                    comments.extend(c)
                    strings.extend(s)
            n_gems += 1
            n_comments += len(comments)
            n_strings += len(strings)
            rec = {
                "gem": gem_dir.name,
                "comments": comments,
                "strings": strings,
                "text": "\n".join(comments + strings),
            }
            out.write(json.dumps(rec) + "\n")
    print(f"gems={n_gems} comments={n_comments} strings={n_strings} -> {out_path}")


if __name__ == "__main__":
    sys.exit(main())
