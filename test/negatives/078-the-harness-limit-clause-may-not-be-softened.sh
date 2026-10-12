#!/usr/bin/env bash
# name: Negative self-test (the harness-limit clause may not be softened)
set -eu
rm -rf /tmp/clause2-copy && cp -R . /tmp/clause2-copy
python3 - <<'EOF'
p = "/tmp/clause2-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
assert "Claude Code only" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("Claude Code only", "available everywhere"))
EOF
if python3 /tmp/clause2-copy/test/validate.py; then
  echo "ERROR: validator passed continuity.md claiming the loop primitive is universal — a run that reports itself as looping while nothing is scheduled claims a capability it does not have"
  exit 1
else
  echo "OK: the harness limit is stated, not implied"
fi
