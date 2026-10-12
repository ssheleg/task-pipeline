#!/usr/bin/env bash
# name: Negative self-test (the holds disclosure is given a direction)
set -eu
rm -rf /tmp/res2-copy && cp -R . /tmp/res2-copy
python3 - <<'EOF'
p = "/tmp/res2-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = 'is never a target'
assert n in t, "PLANT DID NOT LAND: res2"
_planted = t.replace(n, 'is the goal', 1)
assert _planted != t, "PLANT DID NOT LAND: res2"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res2-copy/test/validate.py 2>&1 | grep -q 'no longer declared a non-target'; then
  echo "OK: validator FAILs — a disclosure that acquires a direction is rejected"
else
  echo "ERROR: holds: became a target and nothing objected"
  exit 1
fi
