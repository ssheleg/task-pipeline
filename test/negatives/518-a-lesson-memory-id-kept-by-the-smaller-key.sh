#!/usr/bin/env bash
# name: Negative self-test (a lesson memory id kept by the smaller key)
set -eu
rm -rf /tmp/r14-smaller-copy && cp -R . /tmp/r14-smaller-copy
python3 - <<'EOF'
# Round 14, L1: the earlier holder keeps the id, not the smaller key. Keep the smaller key.
p = "/tmp/r14-smaller-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            keep = (sorted(projects & first.get(base, set())) or sorted(projects))[0]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            keep = sorted(projects)[0]\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='M: one id never stays on two live projects; the earlier holder keeps it'
out=$(python3 /tmp/r14-smaller-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-smaller-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed the smaller key taking the id from its earlier holder"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the earlier holder keeps the id"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
