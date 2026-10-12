#!/usr/bin/env bash
# name: Negative self-test (stage 10 loses criterion 13 entirely)
set -eu
rm -rf /tmp/res15-copy && cp -R . /tmp/res15-copy
python3 - <<'EOF'
# anchor: ^13\. — the criterion NUMBER is the guard's own contract, not this
#   plant's convenience: `test/validate.py` locates the teardown criterion as
#   `^13\.` and its refusal says "stage 10 has no criterion 13". Deriving the
#   number here would make the plant land on whichever criterion happens to be
#   at that position and prove that the guard fired for some other reason —
#   assertion 3, the one hand-rolled probes keep missing. Falsified the moment
#   the guard stops naming 13: the two move together or neither moves.
import os, re
p = "/tmp/res15-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^13\. .*?(?=^\S)", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: res15"
_planted = t[:m.start()] + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND: res15"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res15-copy/test/validate.py 2>&1 | grep -q 'has no criterion 13'; then
  echo "OK: validator FAILs — a give-back written as good intention runs only on the runs that did not need it"
else
  echo "ERROR: the gate criterion was deleted and every text-level check still passed"
  exit 1
fi
