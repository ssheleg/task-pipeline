#!/usr/bin/env bash
# name: Negative self-test (the check rule declared and never required)
set -eu
rm -rf /tmp/b80b-copy && cp -R . /tmp/b80b-copy
python3 - <<'EOF'
import json
p = "/tmp/b80b-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
before = len(n["allOf"])
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
              if "check" not in (deref(c).get("then", {}).get("required") or [])]
assert len(n["allOf"]) == before - 1, "PLANT DID NOT LAND: b80b — no check rule to remove"
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/b80b-copy/test/validate.py; then
  echo "ERROR: a declared-and-optional `check` was accepted — B-080 back one level:
         the doctrine reads a field the graph need not carry"; exit 1
else
  echo "OK: required on every node the verifier will close, parked excepted"
fi
