#!/usr/bin/env bash
# name: Negative self-test (acceptance must close the flow with the hand-back and evidence)
set -eu
rm -rf /tmp/acc-copy && cp -R . /tmp/acc-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/acc-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
import re
c = d["stages"][-1]["gate"]["check"]
assert re.search(r"(?i)hand-back", c), "PLANT DID NOT LAND: the acceptance gate names no hand-back"
d["stages"][-1]["gate"]["check"] = re.sub(r"(?i)hand-back", "close-out", c)
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: acceptance-must-close-the-flow-manua"
EOF
if python3 /tmp/acc-copy/test/validate.py; then
  echo "ERROR: validator passed an acceptance gate with no hand-back"
  exit 1
else
  echo "OK: validator keeps the hand-back in the acceptance gate"
fi
