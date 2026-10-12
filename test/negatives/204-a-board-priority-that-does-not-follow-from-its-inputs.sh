#!/usr/bin/env bash
# name: Negative self-test (a board priority that does not follow from its inputs)
set -eu
rm -rf /tmp/bd5-copy && cp -R . /tmp/bd5-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): pinned to "| 1 | **6** | open" this stopped landing
# the day the board re-derived its ages — the exact release that made the
# priorities honest disarmed the plant that checks them. Pick any OPEN row,
# read its own prio, and write a number that cannot follow from its inputs.
import re
p = "/tmp/bd5-copy/docs/evidence/backlog.md"
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
    c[8] = f" **{pr + 3}** "
    t = t.replace(l, "|".join(c), 1)
    planted = True
    break
assert planted, "PLANT DID NOT LAND: no open row with a numeric prio"
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/bd5-copy/test/validate.py; then
  echo "ERROR: a priority contradicting its own sev/blast/age passed — the hand-assigned number this column replaced"
  exit 1
else
  echo "OK: validator correctly FAILs — the one number a reader is invited to check is checked"
fi
