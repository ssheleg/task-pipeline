#!/usr/bin/env bash
# name: Negative self-test (a lesson project key ignoring init.defaultBranch)
set -eu
rm -rf /tmp/r13-key-default-copy && cp -R . /tmp/r13-key-default-copy
python3 - <<'EOF'
# Round 13, L: with the main worktree's HEAD unborn, init.defaultBranch keys the repository. Skip it.
p = "/tmp/r13-key-default-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if default:\n        refs.append(((), "refs/heads/" + default))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='L: with the main worktree'\''s HEAD unborn, init.defaultBranch keys the repository'
out=$(python3 /tmp/r13-key-default-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-key-default-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an unborn main HEAD refusing its repository's key"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — init.defaultBranch keys the repository"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
