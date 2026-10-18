#!/usr/bin/env bash
# name: Negative self-test (a lesson project key skipping the main worktree HEAD)
set -eu
rm -rf /tmp/r13-key-mainwt-copy && cp -R . /tmp/r13-key-mainwt-copy
python3 - <<'EOF'
# Round 13, L: without origin/HEAD, main or master the key is the main worktree's HEAD. Skip it.
p = "/tmp/r13-key-mainwt-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        refs.append((("--git-dir", common), "HEAD"))  # the main worktree\'s HEAD\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        pass\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='L: without origin/HEAD, main or master, every worktree keys on the main worktree'\''s HEAD'
out=$(python3 /tmp/r13-key-mainwt-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-key-mainwt-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a key following the branch a worktree holds"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — every worktree keys on the main worktree's HEAD"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
