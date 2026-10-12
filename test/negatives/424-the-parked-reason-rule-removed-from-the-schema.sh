#!/usr/bin/env bash
# name: Negative self-test (the parked-reason rule removed from the schema)
set -eu
rm -rf /tmp/gx6-copy && cp -R . /tmp/gx6-copy
python3 - <<'EOF'
import json
p = "/tmp/gx6-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
before = len(n["allOf"])
# Tolerant traversal (B-080 added a branch keyed on `not: {const: parked}`, which
# carries no `const` under `status`; a direct index raises KeyError and the plant
# dies before its own assert can speak).
# B-079 moved the node's conditionals behind `$ref`s in `definitions`, which is
# what proves the checker follows them — and it stopped six plants from finding
# their subject. Follow the reference the way the guard does; the resolved object
# IS the definitions entry, so mutating it still lands in the document.
def deref(o):
    while isinstance(o, dict) and "$ref" in o:
        cur = d
        for part in o["$ref"].lstrip("#/").split("/"):
            cur = cur[part]
        o = cur
    return o
n["allOf"] = [c for c in n["allOf"]
              if deref(c).get("if", {}).get("properties", {}).get("status", {}).get("const") != "parked"]
assert len(n["allOf"]) == before - 1, "PLANT DID NOT LAND: gx6 — no parked rule to remove"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx6-copy/test/validate.py; then
  echo "ERROR: a schema letting a parked node carry no reason was accepted — REQ-012"; exit 1
else
  echo "OK: parked-without-a-reason is refused by the schema, not only by park"
fi
