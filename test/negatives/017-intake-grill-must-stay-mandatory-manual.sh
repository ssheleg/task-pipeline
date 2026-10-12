#!/usr/bin/env bash
# name: Negative self-test (intake grill must stay mandatory + manual)
set -eu
rm -rf /tmp/grill-copy && cp -R . /tmp/grill-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/grill-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
d["stages"][0]["gate"]["type"] = "auto"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: intake-grill-must-stay-mandatory-man"
EOF
if python3 /tmp/grill-copy/test/validate.py; then
  echo "ERROR: validator passed a non-manual intake-grill gate"
  exit 1
else
  echo "OK: validator keeps the intake grill mandatory and operator-confirmed"
fi
