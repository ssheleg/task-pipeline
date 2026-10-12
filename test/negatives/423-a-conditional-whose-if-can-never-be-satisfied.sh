#!/usr/bin/env bash
# name: Negative self-test (a conditional whose `if` can never be satisfied)
set -eu
rm -rf /tmp/gx9-copy && cp -R . /tmp/gx9-copy
python3 - <<'EOF'
import json
p = "/tmp/gx9-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
# B-079 moved the conditionals behind `$ref`s in `definitions`. Follow the
# reference the way the guard does — the resolved object IS the definitions
# entry, so mutating it still lands in the document. Seven plants read
# `node.allOf` inline; this was the seventh, and it died on `KeyError: 'if'`
# after the other six were repaired, which is why the class is written down.
def deref(o):
    while isinstance(o, dict) and "$ref" in o:
        cur = d
        for part in o["$ref"].lstrip("#/").split("/"):
            cur = cur[part]
        o = cur
    return o
conds = [deref(c) for c in d["definitions"]["node"]["allOf"]]
ok = bool(conds) and all("if" in c for c in conds)
assert ok, "PLANT DID NOT LAND: gx9 — no conditionals to disarm"
# additionalProperties is false, so a node can never carry `_never`: both rules
# go inert while every key the check reads is still in place.
for c in conds:
    c["if"]["required"] = ["status", "_never"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx9-copy/test/validate.py; then
  echo "ERROR: two rules that can never fire were accepted — REQ-006 and REQ-012
         both defeated at once"; exit 1
else
  echo "OK: an unsatisfiable `if` is refused"
fi
