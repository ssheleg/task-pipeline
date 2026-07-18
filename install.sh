#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/plugins/task-pipeline/skills/task-pipeline"
DEST="${HOME}/.claude/skills/task-pipeline"
mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
echo "Installed task-pipeline skill -> $DEST"
