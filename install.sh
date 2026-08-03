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

# One channel per agent. This installer writes a PLAIN copy to
# ~/.claude/skills/<id>, and while the Claude Code PLUGIN channel is active that copy
# SHADOWS the plugin — silently serving whatever version was copied, forever. The
# family launcher (sshlg-skills) prunes exactly these copies for that reason, so an
# installer that creates one without saying so undoes the thing it is paired with.
for d in "${HOME}/.claude/plugins/marketplaces/task-pipeline" \
         "${HOME}/.claude/plugins/cache/task-pipeline"; do
  if [[ -e "$d" && "$FORCE" -eq 0 ]]; then
    cat >&2 <<'MSG'
refusing: task-pipeline is already installed as a Claude Code PLUGIN.

A plain copy in ~/.claude/skills/ shadows the plugin and keeps serving the version
it was copied from — the failure this family prunes for. Prefer the plugin:

  claude plugin marketplace update task-pipeline
  claude plugin update task-pipeline@task-pipeline

Rerun with --force if you deliberately want the plain copy instead.
MSG
    exit 3
  fi
done

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
