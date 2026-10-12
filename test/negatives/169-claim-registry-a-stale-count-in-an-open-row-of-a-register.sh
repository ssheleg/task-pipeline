#!/usr/bin/env bash
# name: Negative self-test (claim registry — a stale count in an OPEN row of a register)
set -eu
rm -rf /tmp/cr5c-copy && cp -R . /tmp/cr5c-copy
python3 - <<'EOF'
# `docs/OPEN_QUESTIONS.md` said "the 250 guards" against a workflow defining 390,
# in the exact phrasing the guard class already knew — the registers were simply
# outside the corpus that `docs/DOCMAP.md`'s matrix sends every stated number to.
# Planted in an OPEN board row, not in `docs/OPEN_QUESTIONS.md`. The first
# version used OQ-0002 and went dormant the moment that row gained an ISO date
# in its honesty note — a dated item is a record. On the board the State cell
# is the discriminator instead, so an open row is a live claim whatever dates
# it carries, and this plant cannot be disarmed by editing prose beside it.
# DERIVED, not literal -- which this plant's own comment demanded and its code
# did not do. It matched the whole sentence including "12 registered claim
# classes", so the moment a thirteenth class was registered the needle stopped
# matching and the plant went silent: a check nobody ran, reported green. Anchor
# on the row's ID and on the OPEN state cell, both of which are structure.
import re
p = "/tmp/cr5c-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
rows = [l for l in t.splitlines()
        if re.match(r"^\|\s*B-\d+\s*\|", l) and re.search(r"\|\s*open\s*\|", l)]
assert rows, "PLANT DID NOT LAND: no OPEN board row to plant a stale count in"
row = rows[0]
cells = row.split("|")
cells[2] = cells[2].rstrip() + " Against the 250 guards this suite defines."
t2 = t.replace(row, "|".join(cells), 1)
assert t2 != t, "PLANT DID NOT LAND: the row was not rewritten"
open(p, "w", encoding="utf-8").write(t2)
assert "the 250 guards" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr5c-copy/test/validate.py; then
  echo "ERROR: validator passed a stale total in an OPEN row of a register the doc map names"
  exit 1
else
  echo "OK: validator correctly FAILs — the registers are in the claim-registry corpus"
fi
