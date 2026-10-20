#!/usr/bin/env bash
# name: Negative self-test (the change half of the boundary leaves the description)
set -eu
rm -rf /tmp/rt01-copy && cp -R . /tmp/rt01-copy
python3 - <<'EOF'
p = "/tmp/rt01-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'changes the repository'
assert n in t, "PLANT DID NOT LAND: rt01"
# Every occurrence: since 1.98.0 the routing text is the description plus ## Triggers.
open(p, "w", encoding="utf-8").write(t.replace(n, 'changes the codebase'))
EOF
if python3 /tmp/rt01-copy/test/validate.py 2>&1 | grep -q 'the change half of the boundary is gone'; then
  echo "OK: validator FAILs — a feature must still have a boundary that names it"
else
  echo "ERROR: the description lost the change half and nothing objected"
  exit 1
fi
