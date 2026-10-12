#!/usr/bin/env bash
# name: Negative self-test (an escaped pipe truncating a matrix row's cells)
set -eu
rm -rf /tmp/cw3-copy && cp -R . /tmp/cw3-copy
python3 - <<'EOF'
p = "/tmp/cw3-copy/plugins/task-pipeline/skills/task-pipeline/references/companion-skills.md"
t = open(p, encoding="utf-8").read()
needle = "`playwright-cli open`, `snapshot`"
assert needle in t, "PLANT DID NOT LAND: the playwright row's tool list moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, "`playwright-cli open\\|snapshot`", 1))
EOF
if python3 /tmp/cw3-copy/test/validate.py; then
  echo "ERROR: a pipe inside a cell shifts every later column and the matrix->stages check silently compares nothing"
  exit 1
else
  echo "OK: validator correctly FAILs — no escaped pipe inside a matrix cell"
fi
