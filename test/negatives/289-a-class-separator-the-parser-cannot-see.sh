#!/usr/bin/env bash
# name: Negative self-test (a class separator the parser cannot see)
set -eu
rm -rf /tmp/rt13-copy && cp -R . /tmp/rt13-copy
python3 - <<'EOF'
p = "/tmp/rt13-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'bug hunt/проверь ошибки, production check'
assert n in t, "PLANT DID NOT LAND: rt13"
open(p, "w", encoding="utf-8").write(t.replace(n, 'bug hunt/проверь ошибки and production check', 1))
EOF
if python3 /tmp/rt13-copy/test/validate.py 2>&1 | grep -q 'separator it cannot see'; then
  echo "OK: validator FAILs — a shorter class list is a failure, never a silence"
else
  echo "ERROR: an unparseable separator shrank the class list and nothing objected"
  exit 1
fi
