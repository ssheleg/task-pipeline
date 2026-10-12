#!/usr/bin/env bash
# name: Negative self-test (a ledger shape no reader names)
set -eu
rm -rf /tmp/ledr-copy && cp -R . /tmp/ledr-copy
python3 - <<'EOF'
p = "/tmp/ledr-copy/plugins/task-pipeline/skills/task-pipeline/templates/run.md"
t = open(p, encoding="utf-8").read()
assert "iter: " in t, "PLANT DID NOT LAND: the iteration line moved"
open(p, "w", encoding="utf-8").write(t.replace("iter: ", "cycle:"))
EOF
if python3 /tmp/ledr-copy/test/validate.py; then
  echo "ERROR: a ledger shape nothing reads is a shape nothing writes"
  exit 1
else
  echo "OK: validator correctly FAILs — every declared shape has a named reader"
fi
