#!/usr/bin/env bash
# name: Negative self-test (a lesson add re-key sourcing the twin's own id)
set -eu
rm -rf /tmp/r18-l1add-copy && cp -R . /tmp/r18-l1add-copy
python3 - <<'PY'
# Round 18, L1: put back a lesson add re-key sourcing the twin's own id.
p = "/tmp/r18-l1add-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '({"memory": memory} if not o.get("memory") else'
assert t.count(needle) == 1, "PLANT DID NOT LAND: anchor absent or not unique before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '({"memory": memory, "rekeyedFrom": o["project"]} if not o.get("memory") else', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
PY
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect="r18 L1 add: a twin's own id is given no source by a re-key"
out=$(python3 /tmp/r18-l1add-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r18-l1add-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a lesson add re-key sourcing the twin's own id"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, an add re-key sources only an id it moved"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
