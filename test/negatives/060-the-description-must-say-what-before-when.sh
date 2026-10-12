#!/usr/bin/env bash
# name: Negative self-test (the description must say WHAT before WHEN)
set -eu
rm -rf /tmp/desc-copy && cp -R . /tmp/desc-copy
python3 - <<'EOF'
import re
p = "/tmp/desc-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
t2 = re.sub(r'^description: ".*?"$',
            'description: "Use when running a substantial task через полный цикл."',
            t, count=1, flags=re.M | re.S)
assert t2 != t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/desc-copy/test/validate.py; then
  echo "ERROR: validator passed a description that opens with the trigger and never says what the skill does"
  exit 1
else
  echo "OK: validator requires the capability first, then 'Use when …'"
fi
