#!/usr/bin/env bash
# name: Negative self-test (a BARE pipe truncating a matrix row's cells)
set -eu
rm -rf /tmp/cw4-copy && cp -R . /tmp/cw4-copy
python3 - <<'EOF'
p = "/tmp/cw4-copy/plugins/task-pipeline/skills/task-pipeline/references/companion-skills.md"
t = open(p, encoding="utf-8").read()
needle = "`playwright-cli open`, `snapshot`"
assert needle in t, "PLANT DID NOT LAND: the playwright row's tool list moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, "`playwright-cli open|snapshot`", 1))
EOF
if python3 /tmp/cw4-copy/test/validate.py; then
  echo "ERROR: the first draft of this guard tested the escaped form only, and a bare pipe truncates identically"
  exit 1
else
  echo "OK: validator correctly FAILs — the check counts cells, not escapes"
fi
