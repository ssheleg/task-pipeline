#!/usr/bin/env bash
# name: Negative self-test (the explanation exclusion leaves the clause)
set -eu
rm -rf /tmp/rt10-copy && cp -R . /tmp/rt10-copy
python3 - <<'EOF'
p = "/tmp/rt10-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'answering a question, explaining'
assert n in t, "PLANT DID NOT LAND: rt10"
open(p, "w", encoding="utf-8").write(t.replace(n, 'answering a question, describing code', 1))
EOF
if python3 /tmp/rt10-copy/test/validate.py 2>&1 | grep -q 'the explanation exclusion left'; then
  echo "OK: validator FAILs — all three locked exclusions are held, not just the one probed"
else
  echo "ERROR: the explanation exclusion vanished and nothing objected"
  exit 1
fi
