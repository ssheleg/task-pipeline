#!/usr/bin/env bash
# name: Property check (a real date in the Human column is accepted)
set -eu
rm -rf /tmp/vf4-copy && cp -R . /tmp/vf4-copy
python3 - <<'EOF'
p = "/tmp/vf4-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
needle = "| pass | never | — |"
assert needle in t, "PLANT DID NOT LAND: anchor absent"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "| pass | 2026-08-09 | opened the rendered page |", 1))
EOF
if python3 /tmp/vf4-copy/test/validate.py >/dev/null; then
  echo "OK: filling the column is the point of the file, so filling it must not fail the build"
else
  echo "ERROR: recording that a human looked broke the gate — the column would never be filled again"
  exit 1
fi
