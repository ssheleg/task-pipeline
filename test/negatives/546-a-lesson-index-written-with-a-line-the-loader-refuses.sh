#!/usr/bin/env bash
# name: Negative self-test (a lesson index written with a line the loader refuses)
set -eu
rm -rf /tmp/r17-guard-copy && cp -R . /tmp/r17-guard-copy
python3 - <<'EOF'
# Round 17, F1: take away the write guard, so save writes a line the loader refuses.
p = "/tmp/r17-guard-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    bad = _unloadable(entries)\n'
assert t.count(needle) == 1, "PLANT DID NOT LAND: anchor absent or not unique before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    bad = []\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r17 F1: save refuses a line the loader refuses, the index intact'
out=$(python3 /tmp/r17-guard-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r17-guard-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed save writing a line the loader refuses"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, save refuses a line the loader refuses"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
