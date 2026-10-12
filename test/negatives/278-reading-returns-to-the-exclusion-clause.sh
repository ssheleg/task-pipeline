#!/usr/bin/env bash
# name: Negative self-test (reading returns to the exclusion clause)
set -eu
rm -rf /tmp/rt03-copy && cp -R . /tmp/rt03-copy
python3 - <<'EOF'
p = "/tmp/rt03-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'explaining code, a typo'
assert n in t, "PLANT DID NOT LAND: rt03"
open(p, "w", encoding="utf-8").write(t.replace(n, 'explaining or reading code, a typo', 1))
EOF
if python3 /tmp/rt03-copy/test/validate.py 2>&1 | grep -q 'SKILL.md description: reading is named as an exclusion again'; then
  echo "OK: validator FAILs — reading is the opening move of every findings class"
else
  echo "ERROR: reading came back to the exclusions and nothing objected"
  exit 1
fi
