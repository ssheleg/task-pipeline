#!/usr/bin/env bash
# name: Negative self-test (the axis list moved out from under its own guard)
set -eu
rm -rf /tmp/axis3-copy && cp -R . /tmp/axis3-copy
python3 - <<'EOF'
p = "/tmp/axis3-copy/plugins/task-pipeline/skills/task-pipeline/references/audit.md"
t = open(p, encoding="utf-8").read()
needle = "### 2. Every pass changes the axis, not the effort"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "### 2. Rotating the search", 1))
assert "Every pass changes the axis" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis3-copy/test/validate.py; then
  echo "ERROR: validator passed with its axis source of truth unfindable — a guard silently checking nothing"
  exit 1
else
  echo "OK: validator correctly FAILs — a guard that lost its source says so instead of passing"
fi
