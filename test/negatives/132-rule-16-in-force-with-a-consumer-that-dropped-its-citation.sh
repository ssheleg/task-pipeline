#!/usr/bin/env bash
# name: Negative self-test (rule 16 in force with a consumer that dropped its citation)
set -eu
rm -rf /tmp/r16-copy && cp -R . /tmp/r16-copy
python3 - <<'EOF'
p = "/tmp/r16-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
needle = "Each iteration re-measures the work-list"
assert needle in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "Iterations carry the work-list"))
EOF
if python3 /tmp/r16-copy/test/validate.py; then
  echo "ERROR: validator passed a run mode that never re-measures the work-list"
  exit 1
else
  echo "OK: validator correctly FAILs — a rule-16 consumer dropped its citation"
fi
