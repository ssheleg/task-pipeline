#!/usr/bin/env bash
# name: Negative self-test (a run that cannot be established needs its own state)
set -eu
rm -rf /tmp/ci02-copy && cp -R . /tmp/ci02-copy
python3 - <<'EOF'
p = "/tmp/ci02-copy/plugins/task-pipeline/skills/task-pipeline/references/conventions.md"
t = open(p, encoding="utf-8").read()
assert "**no run found**" in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace("**no run found**", "**probably fine**"))
EOF
if python3 /tmp/ci02-copy/test/validate.py; then
  echo "ERROR: validator passed with the 'no run found' state removed"
  exit 1
else
  echo "OK: validator correctly FAILs — a run that cannot be established needs its own state"
fi
