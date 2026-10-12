#!/usr/bin/env bash
# name: Negative self-test (a matrix row that derives no stage at all)
set -eu
rm -rf /tmp/cw5-copy && cp -R . /tmp/cw5-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the stage number the row derives is exactly what
# the release renumbering the stage list would move, and the plant would
# then mutate nothing while reporting green. Read the number out of the row.
import re
p = "/tmp/cw5-copy/plugins/task-pipeline/skills/task-pipeline/references/companion-skills.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"and `finish` for the stage-\d+ multi-repository close-out", t)
assert m, "PLANT DID NOT LAND: the agent-sync row's stage reference moved"
open(p, "w", encoding="utf-8").write(
    t.replace(m.group(0), "and `finish` for the multi-repository close-out", 1))
EOF
if python3 /tmp/cw5-copy/test/validate.py; then
  echo "ERROR: a row naming no stage leaves the matrix->stages check standing over an empty set, reporting agreement"
  exit 1
else
  echo "OK: validator correctly FAILs — every matrix row derives at least one stage"
fi
