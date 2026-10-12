#!/usr/bin/env bash
# name: Negative self-test (the stage-4 gate stops reading the Carries cells)
set -eu
rm -rf /tmp/fe3-copy && cp -R . /tmp/fe3-copy
python3 - <<'EOF'
import re
p = "/tmp/fe3-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## GATE \(auto\).*", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: fe3 — no GATE section"
_gate = re.sub(r"[Cc]arries", "listed", m.group(0))
_planted = t[:m.start()] + _gate
assert _planted != t, "PLANT DID NOT LAND: fe3"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fe3-copy/test/validate.py 2>&1 | grep -q "the gate does not read the .Carries. cells"; then
  echo "OK: validator FAILs — a column no gate reads is decoration"
else
  echo "ERROR: the gate can stop reading the column and the suite stays green"
  exit 1
fi
