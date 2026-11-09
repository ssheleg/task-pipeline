#!/usr/bin/env bash
# name: Negative self-test (an agent_surface outside the three profiles accepted)
set -eu
rm -rf /tmp/agt5-copy && cp -R . /tmp/agt5-copy
python3 - <<'EOF2'
p = "/tmp/agt5-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = 'if "agent_surface" in n and n["agent_surface"] not in AGENT_SURFACES:'
assert t.count(needle) == 1, "PLANT DID NOT LAND: agt5: the anchor moved or multiplied"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'if False:', 1))
EOF2
if python3 /tmp/agt5-copy/test/graph_test.py >/dev/null 2>&1; then
  echo "ERROR: a typo in agent_surface validated and would silently owe nothing"; exit 1
else
  echo "OK: graph_test.py FAILs: validate refuses an agent_surface outside public, internal and library"
fi
