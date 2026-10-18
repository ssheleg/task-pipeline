#!/usr/bin/env bash
# name: Negative self-test (a lesson memory id kept by the later holder)
set -eu
rm -rf /tmp/r13-earlier-holder-copy && cp -R . /tmp/r13-earlier-holder-copy
python3 - <<'EOF'
# Round 13, M/M2: the earlier holder keeps the id. Keep it on the later one.
p = "/tmp/r13-earlier-holder-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            keep = (sorted(projects & first.get(base, set())) or sorted(projects))[0]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            keep = (sorted(projects - first.get(base, set())) or sorted(projects))[0]\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='M: one id never stays on two live projects; the earlier holder keeps it'
out=$(python3 /tmp/r13-earlier-holder-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-earlier-holder-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed the later holder taking the id"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the project that held the id first keeps it"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
