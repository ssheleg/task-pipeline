#!/usr/bin/env bash
# name: Negative self-test (every node made to owe the agent tier)
set -eu
rm -rf /tmp/agt4-copy && cp -R . /tmp/agt4-copy
python3 - <<'EOF2'
p = "/tmp/agt4-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = 'if asurf in AGENT_REQUIRED and AGENT_TIER not in reports:'
assert t.count(needle) == 1, "PLANT DID NOT LAND: agt4: the anchor moved or multiplied"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'if AGENT_TIER not in reports:', 1))
EOF2
if python3 /tmp/agt4-copy/test/graph_test.py >/dev/null 2>&1; then
  echo "ERROR: a node that owes no agent reading was refused without one"; exit 1
else
  echo "OK: graph_test.py FAILs: only a public or internal agent surface owes the agent tier; a node not owing it passes"
fi
