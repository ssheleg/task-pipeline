#!/usr/bin/env bash
# name: Negative self-test (the seeded gate must read BOTH register shapes)
set -eu
rm -rf /tmp/blindadr-copy && cp -R . /tmp/blindadr-copy
python3 - <<'EOF'
p = "/tmp/blindadr-copy/plugins/task-pipeline/skills/task-pipeline/templates/docgate.sh"
s = open(p, encoding="utf-8").read()
old = 'elif [ "$have_adr" = "1" ]; then'
assert old in s, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(s.replace(old, "elif false; then", 1))
EOF
if python3 /tmp/blindadr-copy/test/validate.py; then
  echo "ERROR: validator passed a gate blind to the ADR shape — every section goes dormant, dormant is green, and a populated register sits behind a passing gate"
  exit 1
else
  echo "OK: validator requires the seeded gate to report its shape and run live checks on both"
fi
