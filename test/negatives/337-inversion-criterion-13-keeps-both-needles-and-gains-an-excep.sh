#!/usr/bin/env bash
# name: Negative self-test (INVERSION — criterion 13 keeps both needles and gains an exception clause)
set -eu
rm -rf /tmp/res5-copy && cp -R . /tmp/res5-copy
python3 - <<'EOF'
p = "/tmp/res5-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = 'does not own** is **reported, never ended** — the inventory is machine-wide and\n   the authority is not.'
assert n in t, "PLANT DID NOT LAND: res5"
_planted = t.replace(n, 'does not own** is **reported, never ended** — unless it looks stale, in which\n   case end it and note that you did.', 1)
assert _planted != t, "PLANT DID NOT LAND: res5"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res5-copy/test/validate.py 2>&1 | grep -q 'admits none'; then
  echo "OK: validator FAILs — an exception marker inside a rule that admits none is the defect"
else
  echo "ERROR: the rule was inverted beside its own needle and every keyword check stayed green"
  exit 1
fi
