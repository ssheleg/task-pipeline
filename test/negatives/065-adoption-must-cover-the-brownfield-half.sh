#!/usr/bin/env bash
# name: Negative self-test (adoption must cover the brownfield half)
set -eu
rm -rf /tmp/adopt-copy && cp -R . /tmp/adopt-copy
python3 - <<'EOF'
p = "/tmp/adopt-copy/plugins/task-pipeline/skills/task-pipeline/references/adoption.md"
t = open(p, encoding="utf-8").read()
assert "An existing project" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("An existing project", "A different heading"))
EOF
if python3 /tmp/adopt-copy/test/validate.py; then
  echo "ERROR: validator passed an adoption doctrine with only the greenfield half — the easy one, and not the one a real repository is in"
  exit 1
else
  echo "OK: validator requires both entry conditions and the ratchet-baseline step"
fi
