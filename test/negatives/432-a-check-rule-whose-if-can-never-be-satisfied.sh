#!/usr/bin/env bash
# name: Negative self-test (a check rule whose `if` can never be satisfied)
set -eu
rm -rf /tmp/b80c-copy && cp -R . /tmp/b80c-copy
python3 - <<'EOF'
import json
p = "/tmp/b80c-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
d = json.load(open(p, encoding="utf-8"))
n = d["definitions"]["node"]
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
c = next((r for r in map(deref, n["allOf"])
          if "check" in (r.get("then", {}).get("required") or [])), None)
assert c and c["if"].get("required") == ["status"], "PLANT DID NOT LAND: b80c"
# `additionalProperties: false` means no node can ever carry `impossible`, so the
# rule is stated and inert. The same trick defeated the first parked_reason guard.
c["if"]["required"] = ["status", "impossible"]
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
EOF
if python3 /tmp/b80c-copy/test/validate.py; then
  echo "ERROR: a rule that can never fire was read as a rule — B-080, and the
         schema stays green while every node escapes it"; exit 1
else
  echo "OK: an `if` is accepted only when it constrains the status and nothing else"
fi
