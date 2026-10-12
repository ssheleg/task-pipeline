#!/usr/bin/env bash
# name: Negative self-test (a verb locked by the design never reaches the surface)
set -eu
rm -rf /tmp/rt05-copy && cp -R . /tmp/rt05-copy
python3 - <<'EOF'
p = "/tmp/rt05-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'внедрить, перевести'
assert n in t, "PLANT DID NOT LAND: rt05"
open(p, "w", encoding="utf-8").write(t.replace(n, 'внедрить', 1))
EOF
if python3 /tmp/rt05-copy/test/validate.py 2>&1 | grep -q 'locked by the 2026-08-03 design'; then
  echo "OK: validator FAILs — this is exactly how перевести sat unshipped for a week"
else
  echo "ERROR: a locked verb vanished and nothing objected"
  exit 1
fi
