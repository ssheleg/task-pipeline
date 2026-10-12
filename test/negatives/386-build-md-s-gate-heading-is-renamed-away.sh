#!/usr/bin/env bash
# name: Negative self-test (build.md's GATE heading is renamed away)
set -eu
rm -rf /tmp/cv9-copy && cp -R . /tmp/cv9-copy
python3 - <<'EOF'
p = "/tmp/cv9-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
old = "## GATE (auto)"
assert old in t, "PLANT DID NOT LAND: cv9 — no GATE heading"
open(p, "w", encoding="utf-8").write(t.replace(old, "## Exit criteria", 1))
EOF
if python3 /tmp/cv9-copy/test/validate.py 2>&1 | grep -q "references/build.md: no .GATE (auto). section"; then
  echo "OK: validator FAILs — a section-scoped criterion goes silent when its section is renamed"
else
  echo "ERROR: the None branch of a _section() site is unproven"
  exit 1
fi
