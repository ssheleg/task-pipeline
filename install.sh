#!/usr/bin/env bash
# Installs the plugin's three skills (task-pipeline, evidence-docs, project-audit) and the
# /task-pipeline command into ~/.claude, and names what a plain copy cannot carry.
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

# 1. skills — all three the plugin ships. task-pipeline names evidence-docs as its doc
# doctrine and runs project-audit as wave 0's sidecar; a plain install that copied one of
# three left both names resolving to nothing (USR-007).
for SKILL in task-pipeline evidence-docs project-audit; do
  SRC="$HERE/plugins/task-pipeline/skills/$SKILL"
  DEST="${HOME}/.claude/skills/$SKILL"
  if [[ ! -f "$SRC/SKILL.md" ]]; then
    echo "error: $SRC is missing — corrupted checkout?" >&2
    exit 1
  fi
  if [[ -e "$DEST" && "$FORCE" -eq 0 ]]; then
    echo "skip: skill already installed at $DEST (rerun with --force to overwrite)"
    continue
  fi
  # Transactional install (FIX-UP-05.02): stage on the same filesystem, then
  # swap. A crash mid-copy leaves the ACTIVE install intact, not a partial tree.
  mkdir -p "$(dirname "$DEST")"
  STAGING="${DEST}.staging.$$"
  rm -rf "$STAGING"
  trap 'rm -rf "$STAGING"' EXIT
  cp -R "$SRC" "$STAGING"
  if [[ -e "$DEST" ]]; then rm -rf "${DEST}.prev.$$"; mv "$DEST" "${DEST}.prev.$$"; fi
  mv "$STAGING" "$DEST"
  rm -rf "${DEST}.prev.$$"
  trap - EXIT
  printf 'Installed %-15s skill -> %s\n' "$SKILL" "$DEST"
done

# 2. slash command (so /task-pipeline works for the plain-skill install too)
CMD_SRC="$HERE/plugins/task-pipeline/commands/task-pipeline.md"
CMD_DEST="${HOME}/.claude/commands/task-pipeline.md"
if [[ -e "$CMD_DEST" && "$FORCE" -eq 0 ]]; then
  echo "skip: command already installed at $CMD_DEST (rerun with --force to overwrite)"
else
  mkdir -p "$(dirname "$CMD_DEST")"
  CMD_STAGING="${CMD_DEST}.staging.$$"
  trap 'rm -f "$CMD_STAGING"' EXIT
  cp "$CMD_SRC" "$CMD_STAGING"
  mv "$CMD_STAGING" "$CMD_DEST"          # atomic rename, never a partial write
  trap - EXIT
  echo "Installed /task-pipeline command -> $CMD_DEST"
fi

# What a plain copy cannot carry, said out loud: the role agents and the hooks are Claude
# Code PLUGIN capabilities. The doctrine names `task-pipeline:verifier` and the hooks by
# file; an operator on this path would otherwise find names that resolve to nothing.
AGENTS="$HERE/plugins/task-pipeline/agents"
HOOKS="$HERE/plugins/task-pipeline/hooks"
N_AGENTS=0; HOOK_NAMES=""
if [ -d "$AGENTS" ]; then N_AGENTS="$(ls -1 "$AGENTS" 2>/dev/null | wc -l | tr -d ' ')"; fi
if [ -d "$HOOKS" ]; then
  HOOK_NAMES="$(cd "$HOOKS" && ls -1 ./*.sh 2>/dev/null | sed 's|^\./||; s|\.sh$||' | paste -sd ',' - | sed 's/,/, /g')"
fi
if [ "$N_AGENTS" -gt 0 ] || [ -n "$HOOK_NAMES" ]; then
  echo ""
  echo "Not installed — Claude Code plugin capabilities a plain copy cannot carry:"
  [ "$N_AGENTS" -gt 0 ] && echo "  - plugins/task-pipeline/agents/ ($N_AGENTS role agents): every role still runs, on the"
  [ "$N_AGENTS" -gt 0 ] && echo "    main thread instead of in its own context — context and speed, not doctrine."
  [ -n "$HOOK_NAMES" ] && echo "  - hooks: $HOOK_NAMES. Without them the gates"
  [ -n "$HOOK_NAMES" ] && echo "    are checked by the doctrine and the run ledger, not by the harness."
  echo "  For both, install the plugin instead (then remove these plain copies):"
  echo "    claude plugin marketplace add ssheleg/task-pipeline"
  echo "    claude plugin install task-pipeline@task-pipeline"
  echo "  Optional companion for checkpoints, handoffs and shared lessons: Project Observatory,"
  echo "    https://github.com/passioncode-ai/project-observatory-dashboard (README: Install, MCP)."
fi
