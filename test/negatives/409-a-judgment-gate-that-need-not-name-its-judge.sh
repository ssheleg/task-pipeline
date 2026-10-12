#!/usr/bin/env bash
# name: Negative self-test (a judgment gate that need not name its judge)
set -eu
rm -rf /tmp/jdg1-copy && cp -R . /tmp/jdg1-copy
python3 - <<'EOF'
import json
p = "/tmp/jdg1-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
d = json.load(open(p, encoding="utf-8"))
def gate(o):
    if isinstance(o, dict):
        if "type" in (o.get("properties") or {}) and "check" in (o.get("required") or []):
            return o
        for v in o.values():
            r = gate(v)
            if r is not None: return r
    elif isinstance(o, list):
        for v in o:
            r = gate(v)
            if r is not None: return r
g = gate(d)
assert g and g.get("allOf"), "PLANT DID NOT LAND: jdg1 — no judgment rule to remove"
g.pop("allOf")
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/jdg1-copy/test/validate.py; then
  echo "ERROR: a judgment gate needing no judge was accepted — B-076: a ruling with
         no author cannot be weighed for independence, and independence is not a
         property of having a reviewer"; exit 1
else
  echo "OK: the judgment rule is probed by running the schema, not by reading it"
fi
