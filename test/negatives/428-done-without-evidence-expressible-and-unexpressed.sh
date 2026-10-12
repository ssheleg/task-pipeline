#!/usr/bin/env bash
# name: Negative self-test (done without evidence, expressible and unexpressed)
set -eu
rm -rf /tmp/gx3-copy && cp -R . /tmp/gx3-copy
python3 - <<'EOF'
import json
p = "/tmp/gx3-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
# Find the done rule WHEREVER it sits. This plant used to do `del n["if"]`,
# and it stopped landing the moment a second conditional arrived and the pair
# moved into `allOf` — a green step that proved nothing, which is the exact
# class that refused three releases on 2026-08-16.
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
# Carries the MEMBER as well as its resolved form: removing the rule means
# dropping the `$ref` that points at it, not the definition it points to.
conds = ([(n, n, None)] if n.get("if") else []) + [
    (c, deref(c), n["allOf"]) for c in n.get("allOf") or []]
hit = [(member, res, owner) for member, res, owner in conds
       if ((res.get("if") or {}).get("properties") or {}).get("status", {}).get("const") == "done"]
assert hit, "PLANT DID NOT LAND: gx3 — no done rule to remove, inline, in allOf or behind a $ref"
member, res, owner = hit[0]
if owner is None:
    del res["if"]; del res["then"]
else:
    owner.remove(member)
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/gx3-copy/test/validate.py; then
  echo "ERROR: a schema that lets a done node carry no evidence was accepted"; exit 1
else
  echo "OK: done-without-evidence is refused by the schema, not only by a script"
fi
