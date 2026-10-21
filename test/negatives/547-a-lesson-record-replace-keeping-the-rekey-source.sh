#!/usr/bin/env bash
# name: Negative self-test (a lesson record --replace keeping the re-key source)
set -eu
rm -rf /tmp/r18-replace-copy && cp -R . /tmp/r18-replace-copy
python3 - <<'PY'
# Round 18, M1: put back a lesson record --replace keeping the re-key source.
p = "/tmp/r18-replace-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '_given(x, memory) if'
assert t.count(needle) == 1, "PLANT DID NOT LAND: anchor absent or not unique before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'dict(x, memory=memory) if', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
PY
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r18 M1 add: record --replace drops the source of the id it replaced'
out=$(python3 /tmp/r18-replace-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r18-replace-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a lesson record --replace keeping the re-key source"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, an id of its own carries no re-key source"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
