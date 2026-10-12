#!/usr/bin/env bash
# name: Negative self-test (a findings class is missing from the portable routing rule)
set -eu
rm -rf /tmp/rt06-copy && cp -R . /tmp/rt06-copy
python3 - <<'EOF'
p = "/tmp/rt06-copy/plugins/task-pipeline/skills/task-pipeline/templates/routing-rule.md"
t = open(p, encoding="utf-8").read()
n = 'a production check'
assert n in t, "PLANT DID NOT LAND: rt06"
open(p, "w", encoding="utf-8").write(t.replace(n, 'a deployment check', 1))
EOF
if python3 /tmp/rt06-copy/test/validate.py 2>&1 | grep -q 'templates/routing-rule.md: the boundary is stated here too'; then
  echo "OK: validator FAILs — a portable rule must agree with the description"
else
  echo "ERROR: the portable rule lost a class and nothing objected"
  exit 1
fi
