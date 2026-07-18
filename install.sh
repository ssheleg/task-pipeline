#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. skill
SRC="$HERE/plugins/task-pipeline/skills/task-pipeline"
DEST="${HOME}/.claude/skills/task-pipeline"
mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
echo "Installed task-pipeline skill   -> $DEST"

# 2. slash command (so /task-pipeline works for the plain-skill install too)
CMD_SRC="$HERE/plugins/task-pipeline/commands/task-pipeline.md"
CMD_DEST="${HOME}/.claude/commands/task-pipeline.md"
mkdir -p "$(dirname "$CMD_DEST")"
cp "$CMD_SRC" "$CMD_DEST"
echo "Installed /task-pipeline command -> $CMD_DEST"
