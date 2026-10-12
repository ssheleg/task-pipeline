#!/usr/bin/env bash
# name: Negative self-test (the negative self-tests must stay runnable off CI)
set -eu
rm -rf /tmp/portable-copy && cp -R . /tmp/portable-copy
python3 - <<'EOF'
# build the forbidden token at runtime — spelling it literally here would
# make this very file trip the guard it is testing
import os, re, sys
sys.path.insert(0, "/tmp/portable-copy/test")
import negatives
bad = "s" + "ed -i"
# The guard reads every check's BODY through the runner's loader (v1.93.0 moved the
# checks out of the workflow), so the plant goes into a body and is asserted on what
# that loader returns — the value the guard reads, not a diff of the file.
d = "/tmp/portable-copy/test/negatives"
p = os.path.join(d, sorted(x for x in os.listdir(d) if x.endswith(".sh"))[0])
open(p, "a", encoding="utf-8").write(f"{bad} 's/a/b/' x\n")
assert any(re.search(r"\b" + bad + r"\b", s) for _n, s in negatives.load_checks(d)), \
    "PLANT DID NOT LAND: the-negative-self-tests-must-stay-ru"
EOF
if python3 /tmp/portable-copy/test/validate.py; then
  echo "ERROR: validator passed a check with non-portable in-place edits — that breaks the local runner on BSD"
  exit 1
else
  echo "OK: validator keeps the negative self-tests portable"
fi
