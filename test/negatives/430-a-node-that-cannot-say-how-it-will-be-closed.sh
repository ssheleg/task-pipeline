#!/usr/bin/env bash
# name: Negative self-test (a node that cannot say how it will be closed)
set -eu
rm -rf /tmp/b80a-copy && cp -R . /tmp/b80a-copy
python3 - <<'EOF'
import json
p = "/tmp/b80a-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
assert "check" in n["properties"], "PLANT DID NOT LAND: b80a — no `check` to remove"
del n["properties"]["check"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/b80a-copy/test/validate.py; then
  echo "ERROR: a node with nowhere to name its completion test was accepted — B-080,
         and agents/verifier.md tells the verifier to read exactly that field"; exit 1
else
  echo "OK: the field the doctrine reads must exist on the node"
fi
