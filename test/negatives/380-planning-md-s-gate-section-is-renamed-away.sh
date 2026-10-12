#!/usr/bin/env bash
# name: Negative self-test (planning.md's GATE section is renamed away)
set -eu
rm -rf /tmp/fe5-copy && cp -R . /tmp/fe5-copy
python3 - <<'EOF'
p = "/tmp/fe5-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
old = "## GATE (auto)"
assert old in t, "PLANT DID NOT LAND: fe5 — no GATE heading"
open(p, "w", encoding="utf-8").write(t.replace(old, "## Exit criteria", 1))
EOF
if python3 /tmp/fe5-copy/test/validate.py 2>&1 | grep -q "no .GATE (auto). section"; then
  echo "OK: validator FAILs — renaming the section would otherwise disable every criterion read out of it"
else
  echo "ERROR: a section-scoped check goes silent when its section is renamed"
  exit 1
fi
