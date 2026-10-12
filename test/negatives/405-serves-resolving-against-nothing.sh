#!/usr/bin/env bash
# name: Negative self-test (serves resolving against nothing)
set -eu
rm -rf /tmp/cov2-copy && cp -R . /tmp/cov2-copy
python3 - <<'EOF'
import json
p = "/tmp/cov2-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
assert "requirements" in d["required"], "PLANT DID NOT LAND: cov2"
d["required"] = [r for r in d["required"] if r != "requirements"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/cov2-copy/test/validate.py; then
  echo "ERROR: a graph with no frozen REQ set was accepted — B-077: serves then
         resolves against nothing, and that is the one edge between the intent
         graph and the execution graph"; exit 1
else
  echo "OK: the intent side of the relation must exist"
fi
