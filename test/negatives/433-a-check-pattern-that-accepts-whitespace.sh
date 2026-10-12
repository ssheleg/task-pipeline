#!/usr/bin/env bash
# name: Negative self-test (a check pattern that accepts whitespace)
set -eu
rm -rf /tmp/b80d-copy && cp -R . /tmp/b80d-copy
python3 - <<'EOF'
import json
p = "/tmp/b80d-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
assert n["properties"]["check"].get("pattern"), "PLANT DID NOT LAND: b80d"
n["properties"]["check"]["pattern"] = "^.*$"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/b80d-copy/test/validate.py; then
  echo "ERROR: a pattern that accepts the empty string was read as a constraint —
         presence is not behaviour, and `minLength: 1` counts a space"; exit 1
else
  echo "OK: the regex is RUN against whitespace, not inspected"
fi
