#!/usr/bin/env bash
# name: Negative self-test (INVERSION — the holds count acquires a direction while 'never a target' still stands)
set -eu
rm -rf /tmp/res7-copy && cp -R . /tmp/res7-copy
python3 - <<'EOF'
p = "/tmp/res7-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
# DERIVED anchor (B-113): the stage number is structure the stage list can
# renumber, and this plant is about the sentence acquiring a DIRECTION.
import re
m = re.search(r"\*\*Only stage (\d+) requires the count to reach zero\*\*", t)
assert m, "PLANT DID NOT LAND: res7"
_planted = t.replace(m.group(0), "**Every stage should drive the count toward "
                     "zero**, and stage %s requires it" % m.group(1), 1)
assert _planted != t, "PLANT DID NOT LAND: res7"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res7-copy/test/validate.py 2>&1 | grep -q 'acquired a direction'; then
  echo "OK: validator FAILs — a disclosure given a direction is rejected even with its non-target line intact"
else
  echo "ERROR: holds: got a direction three paragraphs below the sentence forbidding one"
  exit 1
fi
