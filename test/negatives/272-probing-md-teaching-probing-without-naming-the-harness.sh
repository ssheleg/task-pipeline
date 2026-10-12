#!/usr/bin/env bash
# name: Negative self-test (probing.md teaching probing without naming the harness)
set -eu
rm -rf /tmp/ph3-copy && cp -R . /tmp/ph3-copy
python3 - <<'EOF'
p = "/tmp/ph3-copy/plugins/task-pipeline/skills/task-pipeline/references/probing.md"
t = open(p, encoding="utf-8").read()
n = "`test/probe.py` does all three"
assert n in t, "PLANT DID NOT LAND: the pointer moved"
open(p, "w", encoding="utf-8").write(t.replace(n, "a harness does all three", 1))
EOF
if python3 /tmp/ph3-copy/test/validate.py; then
  echo "ERROR: the next probe gets hand-rolled for the fourth time"
  exit 1
else
  echo "OK: validator correctly FAILs — the probing doctrine points at the harness"
fi
