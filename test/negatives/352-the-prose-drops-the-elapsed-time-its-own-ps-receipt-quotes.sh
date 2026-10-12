#!/usr/bin/env bash
# name: Negative self-test (the prose drops the elapsed time its own `ps` receipt quotes)
set -eu
rm -rf /tmp/res20-copy && cp -R . /tmp/res20-copy
python3 - <<'EOF'
p = "/tmp/res20-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
# The shape this record actually shipped in for six days: the fenced receipt
# keeps `03:12` and the prose stops accounting for it, so the two lines read as
# one instant. The `ps` block is left intact deliberately — a check answered by
# the receipt it is checking is this section's own founding defect.
n = "three minutes and twelve seconds after the monitor was armed"
assert n in t, "PLANT DID NOT LAND: res20"
_planted = t.replace(n, "a few minutes after the monitor was armed", 1)
assert _planted != t, "PLANT DID NOT LAND: res20"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res20-copy/test/validate.py 2>&1 | grep -q "no sentence outside the block accounts for it"; then
  echo "OK: validator FAILs — an elapsed time nothing outside the fence explains is a record asking to be interpreted"
else
  echo "ERROR: the receipt answered for the prose that was supposed to explain it"
  exit 1
fi
