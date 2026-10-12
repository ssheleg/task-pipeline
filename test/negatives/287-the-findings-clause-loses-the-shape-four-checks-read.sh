#!/usr/bin/env bash
# name: Negative self-test (the findings clause loses the shape four checks read)
set -eu
rm -rf /tmp/rt11-copy && cp -R . /tmp/rt11-copy
python3 - <<'EOF'
p = "/tmp/rt11-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'finding that lands in it: audit'
assert n in t, "PLANT DID NOT LAND: rt11"
open(p, "w", encoding="utf-8").write(t.replace(n, 'finding that lands in it — audit', 1))
EOF
if python3 /tmp/rt11-copy/test/validate.py 2>&1 | grep -q 'no longer has the shape'; then
  echo "OK: validator FAILs — a colon changed to a dash took four checks offline in silence"
else
  echo "ERROR: the clause changed shape and four checks vanished quietly"
  exit 1
fi
