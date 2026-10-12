#!/usr/bin/env bash
# name: Negative self-test (rule 14 must bind the stages that write the targets)
set -eu
rm -rf /tmp/readback-map-copy && cp -R . /tmp/readback-map-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the rule number bound to a stage is renumbered
# whenever a rule retires, and the needle `| 3 Spec | 14` would then match
# nothing — a plant that does not land is a check nobody ran, reported
# green. Read whatever rule the readback map binds to the spec stage.
import re
p = "/tmp/readback-map-copy/plugins/task-pipeline/skills/task-pipeline/references/learned.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^\| 3 Spec \| (\d+)", t, re.M)
assert m, "PLANT DID NOT LAND: the readback map binds no rule to stage 3"
t2 = t[:m.start(1)] + "none" + t[m.end(1):]
assert t2 != t, "PLANT DID NOT LAND: the stage-3 binding was not cleared"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/readback-map-copy/test/validate.py; then
  echo "ERROR: validator passed with rule 14 unmapped at stage 3"
  exit 1
else
  echo "OK: validator requires rule 14 at the stages that write targets"
fi
