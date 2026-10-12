#!/usr/bin/env bash
# name: Negative self-test (INVERSION — the foreign-item boundary keeps its sentence and gains a carve-out)
set -eu
rm -rf /tmp/res18-copy && cp -R . /tmp/res18-copy
python3 - <<'EOF'
p = "/tmp/res18-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = '**A foreign item never becomes spent.**'
assert n in t, "PLANT DID NOT LAND: res18"
_planted = t.replace(n, '**A foreign item never becomes spent**, except where nobody claims it.', 1)
assert _planted != t, "PLANT DID NOT LAND: res18"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res18-copy/test/validate.py 2>&1 | grep -q "exception marker"; then
  echo "OK: validator FAILs — the boundary of the third owner state admits no exception"
else
  echo "ERROR: the third owner state reached outside the project through an appended clause"
  exit 1
fi
