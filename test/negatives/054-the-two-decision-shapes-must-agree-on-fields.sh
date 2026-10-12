#!/usr/bin/env bash
# name: Negative self-test (the two decision shapes must agree on fields)
set -eu
rm -rf /tmp/adrparity-copy && cp -R . /tmp/adrparity-copy
python3 - <<'EOF'
p = "/tmp/adrparity-copy/plugins/task-pipeline/skills/task-pipeline/templates/adr.md"
t = open(p, encoding="utf-8").read()
assert "Consequences / affects" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("Consequences / affects", "Downstream effects"))
EOF
if python3 /tmp/adrparity-copy/test/validate.py; then
  echo "ERROR: validator passed a register and an ADR set that disagree on fields — two shapes of one contract is a fork with extra steps"
  exit 1
else
  echo "OK: validator holds decisions.md and adr.md to one field set"
fi
