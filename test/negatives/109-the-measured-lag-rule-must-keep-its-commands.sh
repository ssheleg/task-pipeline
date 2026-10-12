#!/usr/bin/env bash
# name: Negative self-test (the measured-lag rule must keep its commands)
set -eu
rm -rf /tmp/gs03-copy && cp -R . /tmp/gs03-copy
python3 - <<'EOF'
p = "/tmp/gs03-copy/plugins/task-pipeline/skills/task-pipeline/references/knowledge-graph.md"
t = open(p, encoding="utf-8").read()
assert "git rev-list --count" in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace("git rev-list --count", "look at how old it seems")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/gs03-copy/test/validate.py; then
  echo "ERROR: validator passed with the measured-lag rule missing its counting command"
  exit 1
else
  echo "OK: validator correctly FAILs — the measured-lag rule must keep its commands"
fi
