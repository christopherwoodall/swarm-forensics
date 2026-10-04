#!/usr/bin/env bash
# Download AI Village text tables for the stylometry module.
# Requires: HF_TOKEN in the environment, with dataset access granted.
# Access is reviewed manually at https://huggingface.co/datasets/aidigestorg/ai-village
# Writes to pug-research/stylometry/data/raw/ (untracked).
set -euo pipefail

DEST="$(cd "$(dirname "$0")/data/raw" && pwd)"
mkdir -p "$DEST"

if [ -z "${HF_TOKEN:-}" ]; then
  echo "ERROR: HF_TOKEN is not set." >&2
  exit 1
fi

BASE="https://huggingface.co/datasets/aidigestorg/ai-village/resolve/main"
TABLES="chat_messages.jsonl.gz agent_memories.jsonl.gz agent_goals.jsonl.gz claude_code_messages.jsonl.gz computer_use_turns.jsonl.gz agents.jsonl.gz chat_rooms.jsonl.gz claude_code_sessions.jsonl.gz computer_use_sessions.jsonl.gz events.jsonl.gz summaries.jsonl.gz village_goals.jsonl.gz villages.jsonl.gz"

for t in $TABLES; do
  out="$DEST/$t"
  if [ -f "$out" ]; then
    echo "SKIP $t (exists)"
    continue
  fi
  echo "GET $t"
  code=$(curl -sL -w "%{http_code}" -H "Authorization: Bearer $HF_TOKEN" \
    "$BASE/$t" -o "$out.tmp")
  if [ "$code" = "401" ]; then
    echo "ERROR: 401 Unauthorized. Dataset access not granted for this token." >&2
    echo "Request access at https://huggingface.co/datasets/aidigestorg/ai-village" >&2
    rm -f "$out.tmp"
    exit 2
  fi
  if [ "$code" != "200" ]; then
    echo "ERROR: HTTP $code for $t" >&2
    rm -f "$out.tmp"
    exit 3
  fi
  mv "$out.tmp" "$out"
  sleep 2
done
echo "Done. Files in $DEST"
