#!/usr/bin/env bash
# name: Negative self-test (the whole loop contract is deleted from the schema)
set -eu
rm -rf /tmp/lp09-copy && cp -R . /tmp/lp09-copy
python3 - <<'EOF'
import json
p = "/tmp/lp09-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
d = json.load(open(p, encoding="utf-8"))
assert "loop" in d["definitions"]["run"]["properties"], "PLANT DID NOT LAND: lp09"
del d["definitions"]["run"]["properties"]["loop"]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
EOF
if python3 /tmp/lp09-copy/test/validate.py 2>&1 | grep -q 'no run.loop block at definitions.run.properties.loop'; then
  echo "OK: validator FAILs — a deleted contract is a failure, not a tidy skip line"
else
  echo "ERROR: the entire loop contract vanished and the suite stayed green"
  exit 1
fi
