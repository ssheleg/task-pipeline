#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild asking git again for each origin)
set -eu
rm -rf /tmp/r14-cache-copy && cp -R . /tmp/r14-cache-copy
python3 - <<'EOF'
# Round 14, L2: one git question per (checkout, commit) in a run. Ask every time.
p = "/tmp/r14-cache-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if key not in _RESOLVES:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if True:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='L2: git is asked once per'
out=$(python3 /tmp/r14-cache-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-cache-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild asking git the same question again"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — git is asked once per (checkout, commit)"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
