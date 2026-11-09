#!/usr/bin/env bash
# name: Negative self-test (a library node made to owe the agent tier)
set -eu
rm -rf /tmp/agt2-copy && cp -R . /tmp/agt2-copy
python3 - <<'EOF2'
p = "/tmp/agt2-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = 'AGENT_REQUIRED = ("public", "internal")'
assert t.count(needle) == 1, "PLANT DID NOT LAND: agt2: the anchor moved or multiplied"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'AGENT_REQUIRED = ("public", "internal", "library")', 1))
EOF2
if python3 /tmp/agt2-copy/test/graph_test.py >/dev/null 2>&1; then
  echo "ERROR: a library node was made to owe a tier its profile does not need"; exit 1
else
  echo "OK: graph_test.py FAILs: library owes no agent tier; its types, docs and doctests are its proof"
fi
