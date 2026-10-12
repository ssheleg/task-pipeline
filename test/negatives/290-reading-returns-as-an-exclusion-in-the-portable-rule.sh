#!/usr/bin/env bash
# name: Negative self-test (reading returns as an exclusion in the portable rule)
set -eu
rm -rf /tmp/rt15-copy && cp -R . /tmp/rt15-copy
python3 - <<'EOF'
p = "/tmp/rt15-copy/plugins/task-pipeline/skills/task-pipeline/templates/routing-rule.md"
t = open(p, encoding="utf-8").read()
n = 'an explanation, mapping code so a person can read it'
assert n in t, "PLANT DID NOT LAND: rt15"
open(p, "w", encoding="utf-8").write(t.replace(n, 'an explanation, reading code', 1))
EOF
if python3 /tmp/rt15-copy/test/validate.py 2>&1 | grep -q 'reading is named as an exclusion again'; then
  echo "OK: validator FAILs — the defect may not return in the file that ships the rule elsewhere"
else
  echo "ERROR: the portable rule re-excluded reading code and only SKILL.md was checked"
  exit 1
fi
