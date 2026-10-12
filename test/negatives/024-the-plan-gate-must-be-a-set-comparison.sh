#!/usr/bin/env bash
# name: Negative self-test (the plan gate must be a set comparison)
set -eu
rm -rf /tmp/seam-copy && cp -R . /tmp/seam-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/seam-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
for st in d["stages"]:
    if st.get("state") == "plan":
        st["gate"]["check"] = "every spec requirement maps to a task"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: the-plan-gate-must-be-a-set-comparis"
EOF
if python3 /tmp/seam-copy/test/validate.py; then
  echo "ERROR: validator passed a plan gate with no REQ set comparison"
  exit 1
else
  echo "OK: validator requires set equality at the brief-to-plan seam"
fi
