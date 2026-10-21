#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild that always prunes carried origins)
set -eu
rm -rf /tmp/rebuild-prune-copy && cp -R . /tmp/rebuild-prune-copy
python3 - <<'EOF'
# Pruning carried origins is an explicit choice (--prune-carried). Make it the default.
p = "/tmp/rebuild-prune-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                if a.prune_carried and a.prune_carried_reason in (None, rec["carried"]):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                if True:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='a readable empty scope carries the held lesson'
out=$(python3 /tmp/rebuild-prune-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-prune-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild that prunes carried origins without being asked"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — carried origins leave only on --prune-carried"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
