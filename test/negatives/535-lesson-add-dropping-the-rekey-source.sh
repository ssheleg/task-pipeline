#!/usr/bin/env bash
# name: Negative self-test (lesson add dropping the re-key source on a repeat)
set -eu
rm -rf /tmp/r16-merge-copy && cp -R . /tmp/r16-merge-copy
python3 - <<'EOF'
# Round 16: the reclaim. Put back lesson add dropping the re-key source on a repeat.
p = "/tmp/r16-merge-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if old and old.get("memory") and old.get("rekeyedFrom"):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r16 add in X: a repeated add in X keeps rekeyedFrom'
out=$(python3 /tmp/r16-merge-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r16-merge-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a repeated add losing where the id came from"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, a repeated add keeps the source"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
