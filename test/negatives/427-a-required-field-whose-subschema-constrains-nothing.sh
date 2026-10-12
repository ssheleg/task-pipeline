#!/usr/bin/env bash
# name: Negative self-test (a required field whose subschema constrains nothing)
set -eu
rm -rf /tmp/gx2-copy && cp -R . /tmp/gx2-copy
python3 - <<'EOF'
import json
p = "/tmp/gx2-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
o = d["definitions"]["node"]["properties"]["owner"]
assert o.get("minLength"), "PLANT DID NOT LAND: gx2 — owner already unconstrained"
del o["minLength"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx2-copy/test/validate.py; then
  echo "ERROR: owner in required with no minLength was accepted — an empty owner
         satisfies required and dispatches to nobody"; exit 1
else
  echo "OK: a name in required with no constraint is refused"
fi
