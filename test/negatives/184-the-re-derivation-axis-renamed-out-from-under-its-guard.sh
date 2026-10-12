#!/usr/bin/env bash
# name: Negative self-test (the re-derivation axis renamed out from under its guard)
set -eu
rm -rf /tmp/axis6-copy && cp -R . /tmp/axis6-copy
python3 - <<'EOF'
p = "/tmp/axis6-copy/plugins/task-pipeline/skills/task-pipeline/references/audit.md"
t = open(p, encoding="utf-8").read()
needle = "6. **Re-derivation**"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "6. **Second route**", 1))
assert "**Re-derivation**" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis6-copy/test/validate.py; then
  echo "ERROR: validator passed with the guard's subject renamed away — a guard checking nothing"
  exit 1
else
  echo "OK: validator correctly FAILs — a guard whose subject vanished says so"
fi
