#!/usr/bin/env bash
# name: Negative self-test (a parked-reason pattern that accepts the empty string)
set -eu
rm -rf /tmp/gx8-copy && cp -R . /tmp/gx8-copy
python3 - <<'EOF'
import json
p = "/tmp/gx8-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
# Tolerant traversal. B-080 added an `allOf` branch keyed on
# `status: {not: {const: parked}}`, which carries no `const` under `status`, so the
# direct index raised KeyError and this plant died before reaching its own assert.
# A plant that crashes proves nothing — skip a branch shaped differently and let the
# assert below speak when none matches.
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
hit = [deref(c) for c in n["allOf"]]
hit = [c for c in hit
       if c.get("if", {}).get("properties", {}).get("status", {}).get("const") == "parked"]
assert hit, "PLANT DID NOT LAND: gx8 — no parked rule to weaken"
# A pattern is PRESENT and constrains nothing. Checking for the key's existence
# passes this; only running the regex catches it.
hit[0]["then"]["properties"]["parked_reason"]["pattern"] = "^.*$"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx8-copy/test/validate.py; then
  echo "ERROR: a pattern that accepts the empty string was accepted — presence is
         not behaviour, and this is the shape an R-005 read used to defeat it"; exit 1
else
  echo "OK: the pattern is run, not read"
fi
