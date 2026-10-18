#!/usr/bin/env bash
# name: Negative self-test (a lesson index accepting any re-key source)
set -eu
rm -rf /tmp/r16-shape-copy && cp -R . /tmp/r16-shape-copy
python3 - <<'EOF'
# Round 16: the reclaim. Put back a lesson index accepting any re-key source.
p = "/tmp/r16-shape-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if "rekeyedFrom" in o and not (isinstance(o["rekeyedFrom"], str)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if False and not (isinstance(o.get("rekeyedFrom"), str)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r16: a line with rekeyedFrom not-a-key is set aside'
out=$(python3 /tmp/r16-shape-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r16-shape-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an index line with an impossible rekeyedFrom"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, the loader checks rekeyedFrom"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
