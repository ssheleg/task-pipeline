#!/usr/bin/env bash
# The plain-skill installers deliver every skill the plugin ships, and say what they do not
# (CHANGELOG, Unreleased). Both installers — install.sh and bin/task-pipeline.js — run against a
# fresh HOME made here, so no case can touch the real ~/.claude:
#
#   * a fresh install lists task-pipeline, evidence-docs and project-audit under skills/;
#   * a rerun skips all three, --force reinstalls them;
#   * the notice names the hooks that did not arrive, and the plugin command that brings them;
#   * an installed Claude Code plugin is refused (exit 3), so no plain copy shadows it.
#
# Prints PASS and exits non-zero on the first failure.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/tp-install-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
CASES=0
ok() { CASES=$((CASES + 1)); if ! eval "$1"; then echo "FAIL: $2"; exit 1; fi; }
SKILLS="task-pipeline evidence-docs project-audit"
HOOKS="$(cd "$ROOT/plugins/task-pipeline/hooks" && ls -1 ./*.sh | sed 's|^\./||; s|\.sh$||')"

for kind in sh node; do
  H="$TMP/home-$kind"
  mkdir -p "$H"
  run() {
    if [ "$kind" = sh ]; then HOME="$H" CLAUDE_CONFIG_DIR= bash "$ROOT/install.sh" "$@"
    else HOME="$H" CLAUDE_CONFIG_DIR= node "$ROOT/bin/task-pipeline.js" "$@"; fi
  }
  out="$(run 2>&1)"; rc=$?
  ok '[ "$rc" -eq 0 ]' "$kind: a fresh install exits 0 ($rc): $out"
  for s in $SKILLS; do
    ok '[ -f "$H/.claude/skills/$s/SKILL.md" ]' "$kind: a fresh-HOME install lists skills/$s"
    ok 'cmp -s "$ROOT/plugins/task-pipeline/skills/$s/SKILL.md" "$H/.claude/skills/$s/SKILL.md"' \
       "$kind: skills/$s is the shipped bytes"
  done
  ok '[ -f "$H/.claude/commands/task-pipeline.md" ]' "$kind: the command is installed"
  for h in $HOOKS; do
    ok 'printf "%s" "$out" | grep -q "$h"' "$kind: the notice names the hook $h"
  done
  ok 'printf "%s" "$out" | grep -q "claude plugin install task-pipeline@task-pipeline"' \
     "$kind: the notice gives the plugin command"
  ok '[ ! -e "$H/.claude/hooks" ] && [ ! -e "$H/.claude/settings.json" ]' \
     "$kind: no hook is wired silently into settings"
  out="$(run 2>&1)"
  for s in $SKILLS; do
    ok 'printf "%s" "$out" | grep -q "skip: .*skills/$s"' "$kind: a rerun skips $s"
  done
  echo stale > "$H/.claude/skills/evidence-docs/SKILL.md"
  out="$(run --force 2>&1)"; rc=$?
  ok '[ "$rc" -eq 0 ] && cmp -s "$ROOT/plugins/task-pipeline/skills/evidence-docs/SKILL.md" "$H/.claude/skills/evidence-docs/SKILL.md"' \
     "$kind: --force reinstalls every skill"
  P="$TMP/plugin-$kind"
  mkdir -p "$P/.claude/plugins/cache/task-pipeline"
  if [ "$kind" = sh ]; then out="$(HOME="$P" CLAUDE_CONFIG_DIR= bash "$ROOT/install.sh" 2>&1)"; rc=$?
  else out="$(HOME="$P" CLAUDE_CONFIG_DIR= node "$ROOT/bin/task-pipeline.js" 2>&1)"; rc=$?; fi
  ok '[ "$rc" -eq 3 ] && [ ! -e "$P/.claude/skills" ]' "$kind: an installed plugin is refused and nothing is copied"
done
# A corrupted checkout: every source is checked before anything is copied.
C="$TMP/corrupt"
mkdir -p "$C"
cp -R "$ROOT/install.sh" "$ROOT/bin" "$ROOT/plugins" "$C/"
rm -f "$C/plugins/task-pipeline/skills/project-audit/SKILL.md"
for kind in sh node; do
  H="$TMP/home-corrupt-$kind"; mkdir -p "$H"
  if [ "$kind" = sh ]; then out="$(HOME="$H" CLAUDE_CONFIG_DIR= bash "$C/install.sh" 2>&1)"; rc=$?
  else out="$(HOME="$H" CLAUDE_CONFIG_DIR= node "$C/bin/task-pipeline.js" 2>&1)"; rc=$?; fi
  ok '[ "$rc" -ne 0 ] && [ ! -e "$H/.claude/skills" ]' "$kind: a missing third source installs nothing ($rc)"
done
echo "PASS: installers — $CASES cases"
