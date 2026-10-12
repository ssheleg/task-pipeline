#!/usr/bin/env bash
# name: Negative self-test (the arming point loses the one this release moved to)
set -eu
rm -rf /tmp/lp11-copy && cp -R . /tmp/lp11-copy
python3 - <<'EOF'
import json
p = "/tmp/lp11-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
d = json.load(open(p, encoding="utf-8"))
a = d["definitions"]["run"]["properties"]["loop"]["properties"]["arm"]
assert "after-decomposition" in a["enum"], "PLANT DID NOT LAND: lp11"
a["enum"] = ["preflight"]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
EOF
if python3 /tmp/lp11-copy/test/validate.py 2>&1 | grep -q 'does not offer .after-decomposition'; then
  echo "OK: validator FAILs — the field cannot allow only the point the release moved away from"
else
  echo "ERROR: arm kept only preflight and the field's existence was taken as proof"
  exit 1
fi
