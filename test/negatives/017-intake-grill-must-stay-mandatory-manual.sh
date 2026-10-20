#!/usr/bin/env bash
# name: Negative self-test (intake grill must stay mandatory + name its authorization)
set -eu
rm -rf /tmp/grill-copy && cp -R . /tmp/grill-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/grill-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
c = d["stages"][0]["gate"]["check"]
assert "standing authorization" in c, "PLANT DID NOT LAND: the intake gate names no authorization"
d["stages"][0]["gate"]["check"] = c.replace("standing authorization", "operator's word")
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: intake-grill-must-stay-mandatory-man"
EOF
if python3 /tmp/grill-copy/test/validate.py; then
  echo "ERROR: validator passed an intake gate that names no authorization"
  exit 1
else
  echo "OK: validator keeps the intake grill mandatory and its confirmation named"
fi
