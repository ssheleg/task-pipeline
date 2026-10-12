#!/usr/bin/env bash
# name: Negative self-test (the findings half of the boundary leaves the description)
set -eu
rm -rf /tmp/rt02-copy && cp -R . /tmp/rt02-copy
python3 - <<'EOF'
p = "/tmp/rt02-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'finding that lands in it'
assert n in t, "PLANT DID NOT LAND: rt02"
open(p, "w", encoding="utf-8").write(t.replace(n, 'thing produced by it', 1))
EOF
if python3 /tmp/rt02-copy/test/validate.py 2>&1 | grep -q 'the findings half of the boundary is gone'; then
  echo "OK: validator FAILs — an audit is refused when nothing names it"
else
  echo "ERROR: the description lost the findings half and nothing objected"
  exit 1
fi
