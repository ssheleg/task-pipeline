#!/usr/bin/env bash
# name: Negative self-test (a findings class added with no eval-query alias)
set -eu
rm -rf /tmp/rt09-copy && cp -R . /tmp/rt09-copy
python3 - <<'EOF'
p = "/tmp/rt09-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'PR review/ревью PR —'
assert n in t, "PLANT DID NOT LAND: rt09"
open(p, "w", encoding="utf-8").write(t.replace(n, 'PR review/ревью PR, security review/секьюрити —', 1))
EOF
if python3 /tmp/rt09-copy/test/validate.py 2>&1 | grep -q 'no eval-query alias declared'; then
  echo "OK: validator FAILs — a class with no declared alias would measure nothing"
else
  echo "ERROR: a fifth class slipped in unmapped and the guard reported coverage it never looked for"
  exit 1
fi
