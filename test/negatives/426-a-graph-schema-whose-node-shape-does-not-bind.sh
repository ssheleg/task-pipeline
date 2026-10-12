#!/usr/bin/env bash
# name: Negative self-test (a graph schema whose node shape does not bind)
set -eu
rm -rf /tmp/gx1-copy && cp -R . /tmp/gx1-copy
python3 - <<'EOF'
import json
p = "/tmp/gx1-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
assert d["properties"]["nodes"]["type"] == "array", "PLANT DID NOT LAND: gx1"
# An object map with `items` kept as decoration: `items` constrains arrays
# only, so every node check below it becomes vacuous.
d["properties"]["nodes"] = {"type": "object",
                            "additionalProperties": {"type": "object"},
                            "items": {"$ref": "#/definitions/node"}}
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx1-copy/test/validate.py; then
  echo "ERROR: a node shape that binds nothing was accepted"; exit 1
else
  echo "OK: a non-binding node shape is refused"
fi
