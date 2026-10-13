#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild blind to git worktrees)
set -eu
rm -rf /tmp/rebuild-noworktrees-copy && cp -R . /tmp/rebuild-noworktrees-copy
python3 - <<'EOF'
# Round 8, H1: a feature branch's retro lives in a worktree under .claude/worktrees/, which the walk skips. Stop discovering worktrees.
p = "/tmp/rebuild-noworktrees-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        for wt in _worktrees(repo, problems, repos):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        for wt in []:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-noworktrees-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-noworktrees-copy
  echo "ERROR: lessons_test passed a rebuild that never reads git worktrees"
  exit 1
else
  rm -rf /tmp/rebuild-noworktrees-copy
  echo "OK: lessons_test correctly FAILs — worktrees are discovered"
fi
