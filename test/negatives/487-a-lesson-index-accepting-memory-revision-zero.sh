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
if python3 /tmp/load-mem0-copy/test/lessons_test.py; then
  rm -rf /tmp/load-mem0-copy
  echo "ERROR: lessons_test passed an index line with mem:x@0"
  exit 1
else
  rm -rf /tmp/load-mem0-copy
  echo "OK: lessons_test correctly FAILs — revisions start at 1"
fi
