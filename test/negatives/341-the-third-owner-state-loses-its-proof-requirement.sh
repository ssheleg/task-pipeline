#!/usr/bin/env bash
# name: Negative self-test (the third owner state loses its proof requirement)
set -eu
rm -rf /tmp/res9-copy && cp -R . /tmp/res9-copy
python3 - <<'EOF'
p = "/tmp/res9-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = 'end it **when it is provably spent**'
assert n in t, "PLANT DID NOT LAND: res9"
_planted = t.replace(n, 'end it **when it looks abandoned**', 1)
assert _planted != t, "PLANT DID NOT LAND: res9"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res9-copy/test/validate.py 2>&1 | grep -q 'lost `provably spent`'; then
  echo "OK: validator FAILs — 'provably spent' is a fact and 'looks abandoned' is a guess"
else
  echo "ERROR: an earlier run's residue became deletable on a judgement"
  exit 1
fi
