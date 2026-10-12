#!/usr/bin/env bash
# name: Negative self-test (the fake-edge test is removed from planning.md)
set -eu
rm -rf /tmp/fe1-copy && cp -R . /tmp/fe1-copy
python3 - <<'EOF'
import re
p = "/tmp/fe1-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
_planted = re.sub(r"fake-edge test", "ordering review", t, flags=re.I)
assert _planted != t, "PLANT DID NOT LAND: fe1"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fe1-copy/test/validate.py 2>&1 | grep -q "no fake-edge test"; then
  echo "OK: validator FAILs — a dependency graph with no way to find its fake edges is a list with arrows"
else
  echo "ERROR: the fake-edge test can be renamed away and the gate says nothing"
  exit 1
fi
