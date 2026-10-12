#!/usr/bin/env bash
# name: Negative self-test (an exclusion locked in 2026-08-03 drops out)
set -eu
rm -rf /tmp/rt04-copy && cp -R . /tmp/rt04-copy
python3 - <<'EOF'
p = "/tmp/rt04-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = ', a typo, a one-line edit'
assert n in t, "PLANT DID NOT LAND: rt04"
open(p, "w", encoding="utf-8").write(t.replace(n, '', 1))
EOF
if python3 /tmp/rt04-copy/test/validate.py 2>&1 | grep -q "left the 'Not for:' clause"; then
  echo "OK: validator FAILs — the clause and the NOTRIG evals may not drift"
else
  echo "ERROR: a locked exclusion vanished and nothing objected"
  exit 1
fi
