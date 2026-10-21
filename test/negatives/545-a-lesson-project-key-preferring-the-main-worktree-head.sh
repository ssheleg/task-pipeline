#!/usr/bin/env bash
# name: Negative self-test (a lesson project key preferring the main worktree HEAD to init.defaultBranch)
set -eu
rm -rf /tmp/r17-keyorder-copy && cp -R . /tmp/r17-keyorder-copy
python3 - <<'EOF'
# Round 17, L1: put back the main worktree's HEAD before init.defaultBranch.
p = "/tmp/r17-keyorder-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    default = _git(root, "config", "--get", "init.defaultBranch")\n    if default:\n        refs.append(((), "refs/heads/" + default))\n    if common:\n        refs.append((("--git-dir", common), "HEAD"))  # the main worktree\'s HEAD\n'
assert t.count(needle) == 1, "PLANT DID NOT LAND: anchor absent or not unique before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    default = _git(root, "config", "--get", "init.defaultBranch")\n    if common:\n        refs.append((("--git-dir", common), "HEAD"))  # the main worktree\'s HEAD\n    if default:\n        refs.append(((), "refs/heads/" + default))\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r17 L1: init.defaultBranch keys the repository before the main worktree'
out=$(python3 /tmp/r17-keyorder-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r17-keyorder-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a key following the main worktrees orphan branch past init.defaultBranch"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, init.defaultBranch keys the repository first"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
