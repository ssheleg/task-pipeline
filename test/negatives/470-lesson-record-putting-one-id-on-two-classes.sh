#!/usr/bin/env bash
# name: Negative self-test (lesson record putting one memory id on two class keys)
set -eu
rm -rf /tmp/record-twoclass-copy && cp -R . /tmp/record-twoclass-copy
python3 - <<'EOF'
# Round 10, G1: record refuses an id another class key holds. Accept it: emit for one class then revises the other's store record.
p = "/tmp/record-twoclass-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if others:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='G1: record refuses an id another class key holds, writing nothing'
out=$(python3 /tmp/record-twoclass-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/record-twoclass-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed record putting one id on two class keys"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — record refuses an id another class holds"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
