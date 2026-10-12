#!/usr/bin/env bash
# name: Negative self-test (a ledger shape declared and never shown)
set -eu
rm -rf /tmp/led-copy && cp -R . /tmp/led-copy
python3 - <<'EOF'
p = "/tmp/led-copy/plugins/task-pipeline/skills/task-pipeline/templates/run.md"
t = open(p, encoding="utf-8").read()
assert t.count("touch: src/export.ts") >= 2, "PLANT DID NOT LAND: the Log fence lost its touch lines"
open(p, "w", encoding="utf-8").write(t.replace("touch: src/export.ts", "seen:  src/export.ts"))
EOF
if python3 /tmp/led-copy/test/validate.py; then
  echo "ERROR: a declared line shape with no worked example, and an example with no declaration"
  exit 1
else
  echo "OK: validator correctly FAILs — declared and shown, compared both ways"
fi
