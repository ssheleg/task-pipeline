#!/usr/bin/env bash
# name: Negative self-test (the example reverts to its pre-v1.40 loop block)
set -eu
rm -rf /tmp/lp14-copy && cp -R . /tmp/lp14-copy
python3 - <<'EOF'
import json
p = "/tmp/lp14-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
d = json.load(open(p, encoding="utf-8"))
assert "queue" in d["run"]["loop"], "PLANT DID NOT LAND: lp14"
d["run"]["loop"] = {"mode": "off", "interval": "5m", "command": "/loop"}
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
EOF
if python3 /tmp/lp14-copy/test/validate.py 2>&1 | grep -q 'run.loop has no .queue. — the schema offers it'; then
  echo "OK: validator FAILs — the example is what gets copied, so an absent field is a field nobody discovers"
else
  echo "ERROR: the example lost both new fields and the contract passed"
  exit 1
fi
