#!/usr/bin/env bash
# name: Negative self-test (a shipped code-graph doctrine must reach the stage-9 gate)
set -eu
rm -rf /tmp/graph-copy && cp -R . /tmp/graph-copy
python3 - <<'EOF'
import json, re
p = "/tmp/graph-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
d = json.load(open(p, encoding="utf-8"))
for s in d["stages"]:
    if s.get("state") == "docs-wiki":
        s["gate"]["check"] = re.sub(r"graph", "doc", s["gate"]["check"], flags=re.I)
json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-shipped-code-graph-doctrine-must-r"
EOF
if python3 /tmp/graph-copy/test/validate.py; then
  echo "ERROR: validator passed a stage-9 gate that never mentions the graph — the refresh would be declared where it is not enforced"
  exit 1
else
  echo "OK: validator requires the stage-9 gate to enforce the code-graph refresh"
fi
