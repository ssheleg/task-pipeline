#!/usr/bin/env bash
# name: Negative self-test (a `parked` row naming no branch or commit must fail)
set -eu
# B-58: `open` claims nothing exists; `parked` claims something does, and a row
# that claims it without a ref is how work sat "built and parked" in a session
# scratchpad for two days after being deleted.
rm -rf /tmp/prk1-copy && cp -R . /tmp/prk1-copy
python3 - <<'EOF'
p = "/tmp/prk1-copy/plugins/task-pipeline/skills/task-pipeline/templates/backlog.md"
t = open(p, encoding="utf-8").read()
n = "parked — feat/upload-retry"
assert n in t, "PLANT DID NOT LAND: no parked worked example"
open(p, "w", encoding="utf-8").write(t.replace(n, "parked", 1))
EOF
if python3 /tmp/prk1-copy/test/validate.py 2>&1 | grep -q "names no branch or commit"; then
  echo "OK: validator FAILs — a claim that work exists must say where"
else
  echo "ERROR: a row can claim parked work and name nowhere to find it"
  exit 1
fi
