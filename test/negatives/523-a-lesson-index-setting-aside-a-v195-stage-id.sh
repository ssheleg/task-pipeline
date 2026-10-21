#!/usr/bin/env bash
# name: Negative self-test (a lesson index setting aside a v1.95.0 stage id)
set -eu
rm -rf /tmp/r14-migrate-copy && cp -R . /tmp/r14-migrate-copy
python3 - <<'EOF'
# Round 14, L5: a stage id v1.95.0 accepted is normalised on read. Read it as it is.
p = "/tmp/r14-migrate-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        _migrate_stages(e, notes)\n        if not _entry_shape(e):'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if not _entry_shape(e):', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='L5: a v1.95.0 stage id is normalised on read, not set aside'
out=$(python3 /tmp/r14-migrate-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-migrate-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an upgraded index set aside as corrupt"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — an old stage id is normalised on read"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
