#!/usr/bin/env bash
# name: Negative self-test (a graph conditional dropped from behind its `$ref`)
set -eu
rm -rf /tmp/b79a-copy && cp -R . /tmp/b79a-copy
python3 - <<'EOF'
# B-079: `_conditionals()` recursed into `allOf` and never followed a `$ref`, so a
# schema that factors a rule into `definitions` — legal draft-07, and how a rule
# gets shared — read as a schema with NO conditionals, and both REQ-006 and REQ-012
# were reported missing from a schema that states them. The shipped schema now
# states all three rules behind `$ref`, so this plant only fails if the check
# follows the reference and then reads what is on the other side.
import collections, json
p = "/tmp/b79a-copy/plugins/task-pipeline/skills/task-pipeline/graph.schema.json"
s = json.load(open(p, encoding="utf-8"), object_pairs_hook=collections.OrderedDict)
allof = s["definitions"]["node"]["allOf"]
refs = [x.get("$ref", "") for x in allof]
assert any("rule_done_needs_evidence" in r for r in refs), "PLANT DID NOT LAND: the done-rule is not behind a $ref"
s["definitions"]["node"]["allOf"] = [x for x in allof if "rule_done_needs_evidence" not in x.get("$ref", "")]
open(p, "w", encoding="utf-8").write(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
after = json.dumps(json.load(open(p, encoding="utf-8"))["definitions"]["node"])
assert "rule_done_needs_evidence" not in after, "PLANT DID NOT LAND"
EOF
if python3 /tmp/b79a-copy/test/validate.py; then
  echo "ERROR: validator passed a node schema whose done-implies-evidence rule was removed"
  exit 1
else
  echo "OK: validator correctly FAILs — the conditional check reads through a \$ref"
fi
