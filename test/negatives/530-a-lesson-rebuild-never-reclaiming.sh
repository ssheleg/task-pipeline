#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild never reclaiming a re-keyed id)
set -eu
rm -rf /tmp/r16-rb-copy && cp -R . /tmp/r16-rb-copy
python3 - <<'EOF'
# Round 16: the reclaim. Put back a lesson rebuild never reclaiming a re-keyed id.
p = "/tmp/r16-rb-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        _one_class_per_memory(entries, notes)\n        reclaimed = _reclaim(entries)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        _one_class_per_memory(entries, notes)\n        reclaimed = []\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r16 add in X: a full rebuild reclaims the id for Y'
out=$(python3 /tmp/r16-rb-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r16-rb-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild leaving Y's id on X"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, a rebuild reclaims for Y"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
