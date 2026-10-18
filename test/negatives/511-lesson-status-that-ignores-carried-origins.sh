#!/usr/bin/env bash
# name: Negative self-test (lesson status that ignores carried origins)
set -eu
rm -rf /tmp/rebuild-status-copy && cp -R . /tmp/rebuild-status-copy
python3 - <<'EOF'
# Status counts carried origins (except `checkout holds another project`): a temporarily unreadable root never demotes a lesson. Count only re-derived ones.
p = "/tmp/rebuild-status-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    counted = [o for o in origins if o.get("carried") != CARRY_FOREIGN]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    counted = [o for o in origins if not o.get("carried")]\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='N1: status, projects and seen count the carried origin'
out=$(python3 /tmp/rebuild-status-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-status-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a status computed without carried origins"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — status counts temporarily unavailable origins"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
