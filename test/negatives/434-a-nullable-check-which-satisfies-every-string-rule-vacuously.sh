#!/usr/bin/env bash
# name: Negative self-test (a nullable check, which satisfies every string rule vacuously)
set -eu
rm -rf /tmp/b80e-copy && cp -R . /tmp/b80e-copy
python3 - <<'EOF'
import json
p = "/tmp/b80e-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
assert n["properties"]["check"]["type"] == "string", "PLANT DID NOT LAND: b80e"
n["properties"]["check"]["type"] = ["string", "null"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/b80e-copy/test/validate.py; then
  echo "ERROR: a nullable completion test was accepted — `null` passes every
         string-only assertion without being a check"; exit 1
else
  echo "OK: the field is typed string, so null cannot satisfy it vacuously"
fi
