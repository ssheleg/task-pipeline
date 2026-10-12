#!/usr/bin/env bash
# name: Negative self-test (the teardown keeps its first half and loses the one that protects other agents)
set -eu
rm -rf /tmp/res1-copy && cp -R . /tmp/res1-copy
python3 - <<'EOF'
p = "/tmp/res1-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = '**Tear down what this run started. Report what it did not.**'
assert n in t, "PLANT DID NOT LAND: res1"
_planted = t.replace(n, '**Tear down what this run started.**', 1)
assert _planted != t, "PLANT DID NOT LAND: res1"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res1-copy/test/validate.py 2>&1 | grep -q 'the half that kills another agent'; then
  echo "OK: validator FAILs — 'end what you started' without 'report what you did not' is rejected"
else
  echo "ERROR: the asymmetry vanished and nothing objected — a run may now end another session's work"
  exit 1
fi
