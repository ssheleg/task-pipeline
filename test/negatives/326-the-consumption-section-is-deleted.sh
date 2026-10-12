#!/usr/bin/env bash
# name: Negative self-test (the consumption section is deleted)
set -eu
rm -rf /tmp/ri08-copy && cp -R . /tmp/ri08-copy
python3 - <<'EOF'
p = "/tmp/ri08-copy/plugins/task-pipeline/skills/task-pipeline/references/tdd.md"
t = open(p, encoding="utf-8").read()
n = '## What a case consumes'
assert n in t, "PLANT DID NOT LAND: ri08"
_planted = t.replace(n, '## Suite hygiene', 1)
assert _planted != t, "PLANT DID NOT LAND: ri08"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri08-copy/test/validate.py 2>&1 | grep -q 'no section on what a case consumes'; then
  echo "OK: validator FAILs — a suite that exhausts a production limit is measuring the limit"
else
  echo "ERROR: the rule went missing and nothing objected — a suite that exhausts a production limit is measuring the limit"
  exit 1
fi
