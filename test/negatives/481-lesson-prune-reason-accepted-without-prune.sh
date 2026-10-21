#!/usr/bin/env bash
# name: Negative self-test (lesson --prune-carried-reason accepted without --prune-carried)
set -eu
rm -rf /tmp/prune-alone-copy && cp -R . /tmp/prune-alone-copy
python3 - <<'EOF'
# Round 12: --prune-carried-reason narrows --prune-carried; alone it is a usage error.
p = "/tmp/prune-alone-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if a.cmd == "rebuild" and a.prune_carried_reason and not a.prune_carried:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='LOW: --prune-carried-reason without --prune-carried is a usage error'
out=$(python3 /tmp/prune-alone-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/prune-alone-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a prune reason accepted alone"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the prune reason needs --prune-carried"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
