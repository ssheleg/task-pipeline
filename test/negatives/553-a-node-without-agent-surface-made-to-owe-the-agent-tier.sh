#!/usr/bin/env bash
# name: Negative self-test (a node without agent_surface made to owe the agent tier)
set -eu
rm -rf /tmp/agt3-copy && cp -R . /tmp/agt3-copy
python3 - <<'EOF2'
p = "/tmp/agt3-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = 'asurf = node.get("agent_surface")'
assert t.count(needle) == 1, "PLANT DID NOT LAND: agt3: the anchor moved or multiplied"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'asurf = node.get("agent_surface", "public")', 1))
EOF2
if python3 /tmp/agt3-copy/test/graph_test.py >/dev/null 2>&1; then
  echo "ERROR: an absent field owed the agent tier, so every old graph would stop certifying"; exit 1
else
  echo "OK: graph_test.py FAILs: an absent agent_surface owes nothing and old graphs certify as before"
fi
