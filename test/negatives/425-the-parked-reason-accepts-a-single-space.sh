#!/usr/bin/env bash
# name: Negative self-test (the parked reason accepts a single space)
set -eu
rm -rf /tmp/gx7-copy && cp -R . /tmp/gx7-copy
python3 - <<'EOF'
import json
p = "/tmp/gx7-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
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
hit = [deref(c) for c in d["definitions"]["node"]["allOf"]]
hit = [c for c in hit
       if c.get("if", {}).get("properties", {}).get("status", {}).get("const") == "parked"]
dropped = [c["then"]["properties"]["parked_reason"].pop("pattern", None) for c in hit]
assert any(dropped), "PLANT DID NOT LAND: gx7 — no non-whitespace pattern to drop"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx7-copy/test/validate.py; then
  echo "ERROR: minLength alone accepted — a single space satisfies it, which is the
         exact gap the wave-2 convergence check found between the schema and the gate"; exit 1
else
  echo "OK: a whitespace-only reason is refused by the schema"
fi
