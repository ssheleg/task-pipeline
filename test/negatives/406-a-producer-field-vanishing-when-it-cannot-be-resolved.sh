#!/usr/bin/env bash
# name: Negative self-test (a producer field vanishing when it cannot be resolved)
set -eu
rm -rf /tmp/prd1-copy && cp -R . /tmp/prd1-copy
python3 - <<'EOF'
p = "/tmp/prd1-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = 'return v or f"unavailable: {var} is not set by this harness"'
assert needle in t, "PLANT DID NOT LAND: prd1 — the env fallback moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'return v or ""', 1))
EOF
if python3 /tmp/prd1-copy/test/validate.py; then
  echo "ERROR: a producer block with an empty field was accepted — B-086: a field
         that vanishes when unavailable is indistinguishable from one nobody
         checked, which is the rule every disclosure here follows"; exit 1
else
  echo "OK: the producer block is run, and every field must print with a reason"
fi
