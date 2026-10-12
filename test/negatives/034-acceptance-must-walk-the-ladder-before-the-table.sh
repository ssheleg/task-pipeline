#!/usr/bin/env bash
# name: Negative self-test (acceptance must walk the ladder before the table)
set -eu
rm -rf /tmp/ladder-copy && cp -R . /tmp/ladder-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/ladder-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
d["stages"][-1]["gate"]["check"] = (
    "every REQ has a status; every verified carries evidence; the operator signs off"
)
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: acceptance-must-walk-the-ladder-befo"
EOF
if python3 /tmp/ladder-copy/test/validate.py; then
  echo "ERROR: validator passed an acceptance gate that only compares the REQ list — an absence has one side"
  exit 1
else
  echo "OK: validator requires the ladder walk before the coverage table"
fi
