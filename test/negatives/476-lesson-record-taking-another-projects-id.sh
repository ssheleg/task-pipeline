#!/usr/bin/env bash
# name: Negative self-test (lesson record taking another project's memory id)
set -eu
rm -rf /tmp/record-otherproject-copy && cp -R . /tmp/record-otherproject-copy
python3 - <<'EOF'
# Round 12, C: record refuses an id another project's origin holds. Accept it.
p = "/tmp/record-otherproject-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if holders:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='C: record refuses an id another project'\''s origin holds, naming it'
out=$(python3 /tmp/record-otherproject-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/record-otherproject-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed record putting one id on two projects"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — record refuses another project's id"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
