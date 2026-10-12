#!/usr/bin/env bash
# name: Negative self-test (the seeded ledger template showing `backlog` as settled)
set -eu
rm -rf /tmp/cot-copy && cp -R . /tmp/cot-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the whole row was the needle, so every word of
# the seeded example — its id, its stage, its wording — was a promise the
# template would never be edited. What is under test is a Home cell
# holding a bare `backlog` instead of an id, so read the row by its shape.
import re
p = "/tmp/cot-copy/plugins/task-pipeline/skills/task-pipeline/templates/carryover.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"(?m)^\|.*\| `(B-\d+)` \|\s*$", t)
assert m, "PLANT DID NOT LAND: the template has no worked row homed on a board id"
open(p, "w", encoding="utf-8").write(
    t[:m.start(1) - 1] + "backlog" + t[m.end(1) + 1:])
EOF
if python3 /tmp/cot-copy/test/validate.py; then
  echo "ERROR: the file seeded into every host project taught that a bare `backlog` home is a settled outcome"
  exit 1
else
  echo "OK: validator correctly FAILs — the worked example carries a real board id"
fi
