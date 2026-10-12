#!/usr/bin/env bash
# name: Negative self-test (stage 10's criterion 13 loses the report-do-not-end half)
set -eu
rm -rf /tmp/res3-copy && cp -R . /tmp/res3-copy
python3 - <<'EOF'
p = "/tmp/res3-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = '**reported, never ended**'
assert n in t, "PLANT DID NOT LAND: res3"
_planted = t.replace(n, 'cleaned up as well', 1)
assert _planted != t, "PLANT DID NOT LAND: res3"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res3-copy/test/validate.py 2>&1 | grep -q 'lost one of its halves'; then
  echo "OK: validator FAILs — criterion 13 must carry both halves"
else
  echo "ERROR: the give-back criterion kept one half and nothing objected"
  exit 1
fi
