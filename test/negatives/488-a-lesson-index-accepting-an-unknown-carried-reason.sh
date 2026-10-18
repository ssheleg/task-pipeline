#!/usr/bin/env bash
# name: Negative self-test (a lesson index accepting an unknown carried reason)
set -eu
rm -rf /tmp/load-carried-copy && cp -R . /tmp/load-carried-copy
python3 - <<'EOF'
# Round 11/12: `carried` is one of CARRY_REASONS; any other value makes the line corrupt.
p = "/tmp/load-carried-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if "carried" in o and o["carried"] not in CARRY_REASONS:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='LOW: a line with carried='\''whatever'\'' is rejected by the loader'
out=$(python3 /tmp/load-carried-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/load-carried-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an unknown carried reason"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — carried is checked against the enum"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
