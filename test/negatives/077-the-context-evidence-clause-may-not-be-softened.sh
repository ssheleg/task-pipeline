#!/usr/bin/env bash
# name: Negative self-test (the context-evidence clause may not be softened)
set -eu
rm -rf /tmp/clause1-copy && cp -R . /tmp/clause1-copy
python3 - <<'EOF'
p = "/tmp/clause1-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
c = "**never announce that\nthe context is nearly spent without one of those signals**"
assert c in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace(c, "**stay quiet**"))
EOF
if python3 /tmp/clause1-copy/test/validate.py; then
  echo "ERROR: validator passed continuity.md with the evidence clause removed — without it the rule degrades to a suggestion and the guess comes back"
  exit 1
else
  echo "OK: the evidence clause is contractual"
fi
