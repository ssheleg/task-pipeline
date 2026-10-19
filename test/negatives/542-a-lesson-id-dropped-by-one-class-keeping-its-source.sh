#!/usr/bin/env bash
# name: Negative self-test (a lesson id dropped by the one-class rule keeping its source)
set -eu
rm -rf /tmp/r17-oneclass-copy && cp -R . /tmp/r17-oneclass-copy
python3 - <<'EOF'
# Round 17, F1: put back the one-class rule dropping the id but keeping rekeyedFrom.
p = "/tmp/r17-oneclass-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '`_one_project_per_memory`.\n                o = {k: v for k, v in o.items() if k not in ("memory", "rekeyedFrom")}\n'
assert t.count(needle) == 1, "PLANT DID NOT LAND: anchor absent or not unique before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '`_one_project_per_memory`.\n                o = {k: v for k, v in o.items() if k != "memory"}\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r17 F1: an id dropped by the one-class rule leaves a line the loader reads'
out=$(python3 /tmp/r17-oneclass-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r17-oneclass-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an id dropped by the one-class rule keeping rekeyedFrom"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, an id leaves its second class with its source"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
