#!/usr/bin/env bash
# name: Negative self-test (a waived row that keeps its priority must fail)
set -eu
# A decision is not debt. Two of them reached the top of a board on 2026-08-16
# purely by ageing, and the run that picked them up re-derived both.
rm -rf /tmp/wv1-copy && cp -R . /tmp/wv1-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): pinned to `B-005` this plant went silent the day
# the seeded template renumbered a row — and the independent reader found
# it only because the census could not SEE the needle at all: provenance
# was lost through `enumerate()`. What is under test is a row whose Prio
# cell is cleared, so read that instead of the id.
import re
p = "/tmp/wv1-copy/plugins/task-pipeline/skills/task-pipeline/templates/backlog.md"
lines = open(p, encoding="utf-8").read().split("\n")
_t = next((n for n, ln in enumerate(lines)
           if re.match(r"^\|\s*B-\d+\s*\|", ln)
           and len(ln.split("|")) >= 11
           and ln.split("|")[8].strip() == "\u2014"), None)
assert _t is not None, "PLANT DID NOT LAND: no row with a cleared priority"
c = lines[_t].split("|")
c[8] = " 3 "
lines[_t] = "|".join(c)
open(p, "w", encoding="utf-8").write("\n".join(lines))
EOF
if python3 /tmp/wv1-copy/test/validate.py 2>&1 | grep -q "waived but still carries priority"; then
  echo "OK: validator FAILs — a decision cannot be ranked above real work"
else
  echo "ERROR: a waived row can carry a priority and outrank things to do"
  exit 1
fi
