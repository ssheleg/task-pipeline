#!/usr/bin/env bash
# name: Negative self-test (the routing surface and the doctrine disagree on the ledger field's name)
set -eu
rm -rf /tmp/res11-copy && cp -R . /tmp/res11-copy
python3 - <<'EOF'
p = "/tmp/res11-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
n = 'prints `holds: N`'
assert n in t, "PLANT DID NOT LAND: res11"
_planted = t.replace(n, 'prints `residue: N`', 1)
assert _planted != t, "PLANT DID NOT LAND: res11"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res11-copy/test/validate.py 2>&1 | grep -q 'must agree on a'; then
  echo "OK: validator FAILs — SKILL.md and residue.md must name the same field"
else
  echo "ERROR: SKILL.md told runs to print a field the doctrine does not define, and it shipped that way once"
  exit 1
fi
