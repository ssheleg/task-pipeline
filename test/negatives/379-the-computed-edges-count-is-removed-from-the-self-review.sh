#!/usr/bin/env bash
# name: Negative self-test (the computed Edges count is removed from the self-review)
set -eu
rm -rf /tmp/fe4-copy && cp -R . /tmp/fe4-copy
python3 - <<'EOF'
import re
p = "/tmp/fe4-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
_planted = re.sub(r"(?i)edges:", "arrows-noted:", t)
assert _planted != t, "PLANT DID NOT LAND: fe4"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fe4-copy/test/validate.py 2>&1 | grep -q "states no .Edges.. count"; then
  echo "OK: validator FAILs — every other line in that block is a computed number"
else
  echo "ERROR: the one line that counts deleted edges can vanish unnoticed"
  exit 1
fi
