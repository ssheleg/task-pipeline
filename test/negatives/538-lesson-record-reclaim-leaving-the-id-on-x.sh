#!/usr/bin/env bash
# name: Negative self-test (lesson record reclaim leaving the id on X)
set -eu
rm -rf /tmp/r16-rec-strip-copy && cp -R . /tmp/r16-rec-strip-copy
python3 - <<'EOF'
# Round 16: the reclaim. Put back lesson record reclaim leaving the id on X.
p = "/tmp/r16-rec-strip-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                   if any(x is r for r in reclaim) else\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                   if False else\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r16: Y'\''s record reclaims the id from X'
out=$(python3 /tmp/r16-rec-strip-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r16-rec-strip-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a record reclaim leaving the id on both projects"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, a record reclaim drops the id from X"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
