#!/usr/bin/env bash
# name: Negative self-test (the implementer contract keeps the re-reading clause)
set -eu
rm -rf /tmp/fs11-copy && cp -R . /tmp/fs11-copy
python3 - <<'EOF'
p = "/tmp/fs11-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
assert 'confirmed by re-reading the state it changed' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('confirmed by re-reading the state it changed', "confirmed by the tool's reply")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs11-copy/test/validate.py; then
  echo "ERROR: validator passed with the implementer contract keeps the re-reading clause broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the implementer contract keeps the re-reading clause"
fi
