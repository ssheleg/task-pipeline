#!/usr/bin/env bash
# name: Negative self-test (a revision log that records the change and not the reason)
set -eu
rm -rf /tmp/rev1-copy && cp -R . /tmp/rev1-copy
python3 - <<'EOF'
import json
p = "/tmp/rev1-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
req = d["definitions"]["revision"]["required"]
assert "why" in req, "PLANT DID NOT LAND: rev1 — `why` is already not required"
d["definitions"]["revision"]["required"] = [r for r in req if r != "why"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/rev1-copy/test/validate.py; then
  echo "ERROR: a revision log that records what changed and not why was accepted —
         B-084, and a graph revised for unrecorded reasons can explain its own
         completion by a plan that existed only at the end"; exit 1
else
  echo "OK: a revision without a reason is refused"
fi
