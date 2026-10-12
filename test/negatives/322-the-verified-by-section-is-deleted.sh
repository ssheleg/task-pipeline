#!/usr/bin/env bash
# name: Negative self-test (the verified-by section is deleted)
set -eu
rm -rf /tmp/ri04-copy && cp -R . /tmp/ri04-copy
python3 - <<'EOF'
p = "/tmp/ri04-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = '## A `verified by` name is a claim until it resolves'
assert n in t, "PLANT DID NOT LAND: ri04"
_planted = t.replace(n, '## Naming checks', 1)
assert _planted != t, "PLANT DID NOT LAND: ri04"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri04-copy/test/validate.py 2>&1 | grep -q 'no section requiring a `verified by` name'; then
  echo "OK: validator FAILs — a cell can name a check that does not exist"
else
  echo "ERROR: the rule went missing and nothing objected — a cell can name a check that does not exist"
  exit 1
fi
