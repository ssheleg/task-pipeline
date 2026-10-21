#!/usr/bin/env bash
# name: Negative self-test (a lesson reclaim to a project never read)
set -eu
rm -rf /tmp/r17-reclaim-copy && cp -R . /tmp/r17-reclaim-copy
python3 - <<'EOF'
# Round 17, F2: put back the reclaim to any origin of the source project, read or not.
p = "/tmp/r17-reclaim-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            mine = sorted((y for y in origins if y["project"] == src and y.get("checkouts")\n                           and not y.get("carried")), key=_origin_key)\n'
assert t.count(needle) == 1, "PLANT DID NOT LAND: anchor absent or not unique before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            mine = sorted((y for y in origins if y["project"] == src), key=_origin_key)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r17 F2: a project never read does not reclaim in the run that re-keyed'
out=$(python3 /tmp/r17-reclaim-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r17-reclaim-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a re-keyed id reclaimed by a project never read"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, only a read project reclaims"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
