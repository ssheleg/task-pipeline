#!/usr/bin/env bash
# name: Negative self-test (an agent-surface node certified without the agent tier)
set -eu
rm -rf /tmp/agt1-copy && cp -R . /tmp/agt1-copy
python3 - <<'EOF2'
p = "/tmp/agt1-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = 'if asurf in AGENT_REQUIRED and AGENT_TIER not in reports:'
assert t.count(needle) == 1, "PLANT DID NOT LAND: agt1: the anchor moved or multiplied"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'if False:', 1))
EOF2
if python3 /tmp/agt1-copy/test/graph_test.py >/dev/null 2>&1; then
  echo "ERROR: a public or internal agent surface certified with nobody calling it"; exit 1
else
  echo "OK: graph_test.py FAILs: the agent tier is owed on a public or internal agent surface, and its absence refuses the round"
fi
