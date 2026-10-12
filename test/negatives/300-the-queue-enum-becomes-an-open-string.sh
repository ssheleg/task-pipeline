#!/usr/bin/env bash
# name: Negative self-test (the queue enum becomes an open string)
set -eu
rm -rf /tmp/lp10-copy && cp -R . /tmp/lp10-copy
python3 - <<'EOF'
import json
p = "/tmp/lp10-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
d = json.load(open(p, encoding="utf-8"))
q = d["definitions"]["run"]["properties"]["loop"]["properties"]["queue"]
assert "enum" in q, "PLANT DID NOT LAND: lp10"
del q["enum"]; q["type"] = "string"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
EOF
if python3 /tmp/lp10-copy/test/validate.py 2>&1 | grep -q 'an open string is not a queue'; then
  echo "OK: validator FAILs — an open string accepts the name of a list nobody builds"
else
  echo "ERROR: the queue accepted any string and nothing objected"
  exit 1
fi
