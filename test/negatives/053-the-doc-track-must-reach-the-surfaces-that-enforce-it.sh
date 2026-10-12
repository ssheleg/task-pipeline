#!/usr/bin/env bash
# name: Negative self-test (the doc track must reach the surfaces that enforce it)
set -eu
rm -rf /tmp/anchor-copy && cp -R . /tmp/anchor-copy
python3 - <<'EOF'
import re
p = "/tmp/anchor-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert re.search("propagation", t, re.I), "PLANT MISSED"
open(p, "w", encoding="utf-8").write(re.sub("propagation", "spreading", t, flags=re.I))
EOF
if python3 /tmp/anchor-copy/test/validate.py; then
  echo "ERROR: validator passed with the propagation sweep declared in SKILL.md and absent from stages.md — declared where it is not enforced is inert"
  exit 1
else
  echo "OK: validator holds every surface that enforces stage 9 to the propagation sweep"
fi
