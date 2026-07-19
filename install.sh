#!/usr/bin/env bash
# Installs the task-pipeline skill + /task-pipeline command into ~/.claude.
# Idempotent: skips anything already installed; pass --force to overwrite.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--force]" >&2
  exit 2
fi

# 1. skill
SRC="$HERE/plugins/task-pipeline/skills/task-pipeline"
DEST="${HOME}/.claude/skills/task-pipeline"
if [[ -e "$DEST" && "$FORCE" -eq 0 ]]; then
  echo "skip: skill already installed at $DEST (rerun with --force to overwrite)"
else
  mkdir -p "$(dirname "$DEST")"
  rm -rf "$DEST"
  cp -R "$SRC" "$DEST"
  echo "Installed task-pipeline skill   -> $DEST"
fi

# 2. slash command (so /task-pipeline works for the plain-skill install too)
CMD_SRC="$HERE/plugins/task-pipeline/commands/task-pipeline.md"
CMD_DEST="${HOME}/.claude/commands/task-pipeline.md"
if [[ -e "$CMD_DEST" && "$FORCE" -eq 0 ]]; then
  echo "skip: command already installed at $CMD_DEST (rerun with --force to overwrite)"
else
  mkdir -p "$(dirname "$CMD_DEST")"
  cp "$CMD_SRC" "$CMD_DEST"
  echo "Installed /task-pipeline command -> $CMD_DEST"
fi
