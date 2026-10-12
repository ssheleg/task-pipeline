#!/usr/bin/env bash
# name: Negative self-test (a timeout becomes a slow result again)
set -eu
rm -rf /tmp/ri09-copy && cp -R . /tmp/ri09-copy
python3 - <<'EOF'
p = "/tmp/ri09-copy/plugins/task-pipeline/skills/task-pipeline/references/tdd.md"
t = open(p, encoding="utf-8").read()
n = 'is an unclassified result, not a slow one'
assert n in t, "PLANT DID NOT LAND: ri09"
_planted = t.replace(n, 'is a slow result', 1)
assert _planted != t, "PLANT DID NOT LAND: ri09"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri09-copy/test/validate.py 2>&1 | grep -q 'UNCLASSIFIED result'; then
  echo "OK: validator FAILs — read as slow, it sends a run to investigate the wrong thing"
else
  echo "ERROR: the rule went missing and nothing objected — read as slow, it sends a run to investigate the wrong thing"
  exit 1
fi
