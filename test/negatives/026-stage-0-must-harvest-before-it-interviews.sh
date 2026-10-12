#!/usr/bin/env bash
# name: Negative self-test (stage 0 must harvest before it interviews)
set -eu
rm -rf /tmp/harvest-copy && cp -R . /tmp/harvest-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/harvest-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
d["stages"][0]["gate"]["check"] = "MANDATORY stage — never skipped. One question at a time; the brief is confirmed."
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: stage-0-must-harvest-before-it-inter"
EOF
if python3 /tmp/harvest-copy/test/validate.py; then
  echo "ERROR: validator passed a stage-0 gate with no knowledge harvest"
  exit 1
else
  echo "OK: validator requires the phase-1 harvest and its ledger before the interview"
fi
