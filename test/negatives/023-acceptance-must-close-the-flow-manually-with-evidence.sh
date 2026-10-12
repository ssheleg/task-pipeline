#!/usr/bin/env bash
# name: Negative self-test (acceptance must close the flow, manually, with evidence)
set -eu
rm -rf /tmp/acc-copy && cp -R . /tmp/acc-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/acc-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
d["stages"][-1]["gate"]["type"] = "auto"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: acceptance-must-close-the-flow-manua"
EOF
if python3 /tmp/acc-copy/test/validate.py; then
  echo "ERROR: validator passed a non-manual acceptance gate"
  exit 1
else
  echo "OK: validator keeps acceptance manual — only the asker can confirm"
fi
