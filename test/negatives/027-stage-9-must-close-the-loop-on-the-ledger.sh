#!/usr/bin/env bash
# name: Negative self-test (stage 9 must close the loop on the ledger)
set -eu
rm -rf /tmp/loopback-copy && cp -R . /tmp/loopback-copy
python3 - <<'EOF'
import json, collections
p = "/tmp/loopback-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
for s in d["stages"]:
    if s.get("state") == "docs-wiki":
        s["gate"]["check"] = "docs in sync with code; wiki synced; dangling links fixed"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: stage-9-must-close-the-loop-on-the-l"
EOF
if python3 /tmp/loopback-copy/test/validate.py; then
  echo "ERROR: validator passed a docs stage that never updates what stage 0 read"
  exit 1
else
  echo "OK: validator keeps the harvest→update loop closed"
fi
