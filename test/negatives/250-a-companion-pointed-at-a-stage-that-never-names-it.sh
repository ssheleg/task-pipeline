#!/usr/bin/env bash
# name: Negative self-test (a companion pointed at a stage that never names it)
set -eu
rm -rf /tmp/cw1-copy && cp -R . /tmp/cw1-copy
python3 - <<'EOF'
p = "/tmp/cw1-copy/plugins/task-pipeline/skills/task-pipeline/references/companion-skills.md"
t = open(p, encoding="utf-8").read()
needle = "| stage 3 — the **VISUAL track**"
assert needle in t, "PLANT DID NOT LAND: the visual row moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, "| stage 4 — the **VISUAL track**", 1))
EOF
if python3 /tmp/cw1-copy/test/validate.py; then
  echo "ERROR: the operator is told to install a companion for a stage that has not heard of it"
  exit 1
else
  echo "OK: validator correctly FAILs — the matrix and the stage it points at agree"
fi
