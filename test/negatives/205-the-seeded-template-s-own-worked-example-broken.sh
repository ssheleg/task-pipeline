#!/usr/bin/env bash
# name: Negative self-test (the seeded template's own worked example broken)
set -eu
rm -rf /tmp/bd6-copy && cp -R . /tmp/bd6-copy
python3 - <<'EOF'
# DERIVED anchor (B-113), the sibling of the live-board plant below: the
# template's example carries an Age that this repository re-derives, so
# `| 12 | **2** | open` was one edit from matching nothing. Read an OPEN
# row's own priority and write a number that cannot follow from its inputs.
import re
p = "/tmp/bd6-copy/plugins/task-pipeline/skills/task-pipeline/templates/backlog.md"
t = open(p, encoding="utf-8").read()
planted = False
for l in t.splitlines():
    if not re.match(r"^\|\s*B-\d+\s*\|", l):
        continue
    c = l.split("|")
    if len(c) < 11 or c[9].strip().lower().strip("*") != "open":
        continue
    try:
        pr = int(c[8].strip().strip("*"))
    except ValueError:
        continue
    c[8] = " **%d** " % (pr + 5)
    t = t.replace(l, "|".join(c), 1)
    planted = True
    break
assert planted, "PLANT DID NOT LAND: no open template row with a numeric prio"
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/bd6-copy/test/validate.py; then
  echo "ERROR: the file seeded verbatim into every host project shipped an example that fails its own formula"
  exit 1
else
  echo "OK: validator correctly FAILs — the plant lands in the template, not only in this repo's board"
fi
