#!/usr/bin/env bash
# name: Negative self-test (a findings class is missing from the Cursor rule)
set -eu
rm -rf /tmp/rt07-copy && cp -R . /tmp/rt07-copy
python3 - <<'EOF'
p = "/tmp/rt07-copy/cursor/rules/task-pipeline.mdc"
t = open(p, encoding="utf-8").read()
n = 'PR review'
assert n in t, "PLANT DID NOT LAND: rt07"
open(p, "w", encoding="utf-8").write(t.replace(n, 'merge inspection', -1))
EOF
if python3 /tmp/rt07-copy/test/validate.py 2>&1 | grep -q 'task-pipeline.mdc: the boundary is stated here too'; then
  echo "OK: validator FAILs — the Cursor rule states the same boundary"
else
  echo "ERROR: the Cursor rule lost a class and nothing objected"
  exit 1
fi
