#!/usr/bin/env bash
# name: Negative self-test (the green-probe section keeps its heading and loses its rule)
set -eu
rm -rf /tmp/ri03b-copy && cp -R . /tmp/ri03b-copy
python3 - <<'EOF'
p = "/tmp/ri03b-copy/plugins/task-pipeline/skills/task-pipeline/references/probing.md"
t = open(p, encoding="utf-8").read()
n = "asserts its plant landed"
assert n in t, "PLANT DID NOT LAND: ri03b"
# The heading stays. Only the obligation goes — the branch ri03 cannot reach,
# because it renames the heading and stops at the first fail().
_planted = t.replace(n, "is worth writing carefully", 1)
assert _planted != t, "PLANT DID NOT LAND: ri03b"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri03b-copy/test/validate.py 2>&1 | grep -q "the obligation is gone"; then
  echo "OK: validator FAILs — a section emptied to a bare heading keeps none of its rule"
else
  echo "ERROR: the heading survived, the rule did not, and nothing objected"
  exit 1
fi
