#!/usr/bin/env bash
# name: Negative self-test (INVERSION — the foreign lease keeps its sentence and gains a carve-out)
set -eu
rm -rf /tmp/res17-copy && cp -R . /tmp/res17-copy
python3 - <<'EOF'
p = "/tmp/res17-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = '**A lease held by another agent is never released by this run**'
assert n in t, "PLANT DID NOT LAND: res17"
_planted = t.replace(n, '**A lease held by another agent is never released by this run**, unless it has clearly expired', 1)
assert _planted != t, "PLANT DID NOT LAND: res17"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res17-copy/test/validate.py 2>&1 | grep -q "exception marker"; then
  echo "OK: validator FAILs — an absolute rule with a carve-out is the inversion, substring intact"
else
  echo "ERROR: another agent's lease became releasable by appending four words, and every substring check agreed"
  exit 1
fi
