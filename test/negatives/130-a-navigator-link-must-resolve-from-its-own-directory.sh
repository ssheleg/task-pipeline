#!/usr/bin/env bash
# name: Negative self-test (a navigator link must resolve from its own directory)
set -eu
rm -rf /tmp/ed4-copy && cp -R . /tmp/ed4-copy
python3 - <<'EOF'
# The link SHAPE this plant breaks changed with FIX-ED-01.01: evidence-docs
# now ships its own GENERATED copies of these references, so the link that
# used to navigate out of the skill (`../task-pipeline/references/gates.md`)
# is in-set (`references/gates.md`). The RULE is the same one — a link a
# live document claims must resolve from its own directory — so the plant
# follows the link to its new shape rather than asserting a dead one.
p = "/tmp/ed4-copy/plugins/task-pipeline/skills/evidence-docs/SKILL.md"
t = open(p, encoding="utf-8").read()
assert '](references/gates.md)' in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace('](references/gates.md)', '](references/gaits.md)'))
EOF
if python3 /tmp/ed4-copy/test/validate.py; then
  echo "ERROR: validator passed with a navigator link must resolve from its own directory broken"
  exit 1
else
  echo "OK: validator correctly FAILs — a navigator link must resolve from its own directory"
fi
