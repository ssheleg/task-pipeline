#!/usr/bin/env bash
# name: Negative self-test (the machine-readable stage 2 drops the arming)
set -eu
rm -rf /tmp/lp08-copy && cp -R . /tmp/lp08-copy
python3 - <<'EOF'
p = "/tmp/lp08-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
t = open(p, encoding="utf-8").read()
# Replacing only the headline left 'a loop armed earlier' in the same gate
# string, so the guard's substring test still matched. Drop the sentence whole.
n = " THE LOOP'S ARMING STATE IS PRINTED \u2014 armed with its queue and pacing, or not armed with the reason; the queue exists at this stage and a loop armed earlier has nothing to walk."
assert n in t, "PLANT DID NOT LAND: lp08"
open(p, "w", encoding="utf-8").write(t.replace(n, "", 1))
EOF
if python3 /tmp/lp08-copy/test/validate.py 2>&1 | grep -q "does not require the loop's arming state"; then
  echo "OK: validator FAILs — the two statements of one rule may not drift"
else
  echo "ERROR: the example's gate lost the arming while the prose kept it"
  exit 1
fi
