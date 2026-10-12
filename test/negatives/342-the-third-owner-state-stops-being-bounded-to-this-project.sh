#!/usr/bin/env bash
# name: Negative self-test (the third owner state stops being bounded to this project)
set -eu
rm -rf /tmp/res10-copy && cp -R . /tmp/res10-copy
python3 - <<'EOF'
p = "/tmp/res10-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = '**A foreign item never becomes spent.**'
assert n in t, "PLANT DID NOT LAND: res10"
_planted = t.replace(n, '**A foreign item becomes spent eventually.**', 1)
assert _planted != t, "PLANT DID NOT LAND: res10"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res10-copy/test/validate.py 2>&1 | grep -q 'outside the project'; then
  echo "OK: validator FAILs — widening what a run may clean inside its project must not widen it outside"
else
  echo "ERROR: uptime became permission to stop another project's container"
  exit 1
fi
