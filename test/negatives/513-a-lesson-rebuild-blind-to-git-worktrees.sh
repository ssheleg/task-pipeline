#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild blind to git worktrees)
set -eu
rm -rf /tmp/rebuild-noworktrees-copy && cp -R . /tmp/rebuild-noworktrees-copy
python3 - <<'EOF'
# Round 8: a feature branch's retro lives in a worktree under .claude/worktrees/, which the walk skips. Stop discovering worktrees.
p = "/tmp/rebuild-noworktrees-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        for wt in _worktrees(repo, problems):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        for wt in []:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='Q1: a worktree under .claude/worktrees is discovered; its lesson keeps its memory id'
out=$(python3 /tmp/rebuild-noworktrees-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-noworktrees-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild that never reads git worktrees"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — worktrees are discovered"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
