#!/usr/bin/env bash
# name: Negative self-test (a lesson index accepting memory revision zero)
set -eu
rm -rf /tmp/load-mem0-copy && cp -R . /tmp/load-mem0-copy
python3 - <<'EOF'
# Round 11/12: memory revisions start at 1; a line holding mem:x@0 is corrupt. Accept @0.
p = "/tmp/load-mem0-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = 'MEM_RE = re.compile(r"mem:[^@\\s\\"\\\\]+@[1-9][0-9]*")'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'MEM_RE = re.compile(r"mem:[^@\\s\\"\\\\]+@[0-9]+")', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='LOW: a line with memory='\''mem:x@0'\'' is rejected by the loader'
out=$(python3 /tmp/load-mem0-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/load-mem0-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an index line with mem:x@0"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — revisions start at 1"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
