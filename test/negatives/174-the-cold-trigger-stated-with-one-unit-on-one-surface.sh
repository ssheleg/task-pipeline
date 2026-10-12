#!/usr/bin/env bash
# name: Negative self-test (the cold trigger stated with one unit on one surface)
set -eu
rm -rf /tmp/cold-copy && cp -R . /tmp/cold-copy
python3 - <<'EOF'
p = "/tmp/cold-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
needle = "fired in the last five run stamps **or in the last sixty days**"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, "fired in the last five run stamps", 1)
open(p, "w", encoding="utf-8").write(t)
s = open(p, encoding="utf-8").read()
assert "five run stamps **or in the last sixty days**" not in s, "PLANT DID NOT LAND"
EOF
if python3 /tmp/cold-copy/test/validate.py; then
  echo "ERROR: validator passed a cold trigger whose second unit is missing on one surface"
  exit 1
else
  echo "OK: validator correctly FAILs — both units, on every surface that states it"
fi
