#!/usr/bin/env bash
# name: Negative self-test (an unresolvable verified-by name keeps reading verified)
set -eu
rm -rf /tmp/ri05-copy && cp -R . /tmp/ri05-copy
python3 - <<'EOF'
p = "/tmp/ri05-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = 'status **`unknown`**, never `verified`'
assert n in t, "PLANT DID NOT LAND: ri05"
_planted = t.replace(n, 'status noted in the row', 1)
assert _planted != t, "PLANT DID NOT LAND: ri05"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri05-copy/test/validate.py 2>&1 | grep -q 'the status an unresolvable'; then
  echo "OK: validator FAILs — without `unknown` the row keeps reading verified"
else
  echo "ERROR: the rule went missing and nothing objected — without `unknown` the row keeps reading verified"
  exit 1
fi
