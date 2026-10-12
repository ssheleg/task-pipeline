#!/usr/bin/env bash
# name: Negative self-test (the verdict gate and the graph schema must not diverge)
set -eu
rm -rf /tmp/gx5-copy && cp -R . /tmp/gx5-copy
python3 - <<'EOF'
import re
p = ("/tmp/gx5-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py")
t = open(p, encoding="utf-8").read()
# Weaken the gate to the container-only check the first draft had: a list of
# blank strings then passes the gate and is refused by the schema, so `close`
# would write a node the shipped schema rejects.
m = re.search(r"\n        for i, e in enumerate\(v\[\"evidence\"\]\):.*?\n\n", t, re.S)
assert m, "PLANT DID NOT LAND: gx5 — no per-entry evidence check to remove"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "\n\n"))
EOF
if python3 /tmp/gx5-copy/test/graph_test.py; then
  echo "ERROR: the verdict gate may accept evidence the schema refuses"; exit 1
else
  echo "OK: the gate and the schema are held to the same rule"
fi
