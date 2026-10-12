#!/usr/bin/env bash
# name: Negative self-test (non-token stage model must fail)
set -eu
rm -rf /tmp/token-copy && cp -R . /tmp/token-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/token-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
d["stages"][0]["model"] = "some-vendor-model"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: non-token-stage-model-must-fail"
EOF
if python3 /tmp/token-copy/test/validate.py; then
  echo "ERROR: validator passed a stage model that is not a provider-agnostic token"
  exit 1
else
  echo "OK: validator requires provider-agnostic stage model tokens"
fi
