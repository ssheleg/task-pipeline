#!/usr/bin/env bash
# name: Negative self-test (intake must settle the Figma design destination)
set -eu
rm -rf /tmp/dest-copy && cp -R . /tmp/dest-copy
python3 - <<'EOF'
import json, collections, re
p = "/tmp/dest-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
c = d["stages"][0]["gate"]["check"]
d["stages"][0]["gate"]["check"] = re.sub(
    r"; plus, with Figma on, the DESIGN DESTINATION.*?replacement\)", ")", c, flags=re.S)
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: intake-must-settle-the-figma-design"
EOF
if python3 /tmp/dest-copy/test/validate.py; then
  echo "ERROR: validator passed an intake gate that never settles which Figma file, in which team"
  exit 1
else
  echo "OK: validator requires the design destination at intake — a duplicate design file is silent"
fi
