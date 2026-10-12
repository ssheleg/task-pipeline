#!/usr/bin/env bash
# name: Negative self-test (a stale count in an OPEN question, dated beside it)
set -eu
rm -rf /tmp/oqs-copy && cp -R . /tmp/oqs-copy
python3 - <<'EOF'
# The hole this closes was self-inflicted and watched. The honesty note explaining
# that OQ-0002 no longer restates a total put an ISO date in the row, which made the
# whole row a dated record and DISARMED the register plant — the guard went green
# over exactly the stale total it had been written to catch. `OQ-####` now uses the
# status cell, the same discriminator the board uses: `Open` is a live claim
# whatever dates sit beside it.
p = "/tmp/oqs-copy/docs/OPEN_QUESTIONS.md"
t = open(p, encoding="utf-8").read()
anchor = "\n**When one resolves:**"
assert anchor in t, "PLANT DID NOT LAND: anchor absent before edit"
row = "| OQ-9999 | Do the 250 guards still need a probe? Asked 2026-08-20 | operator | nothing | Open |\n"
open(p, "w", encoding="utf-8").write(t.replace(anchor, "\n" + row + anchor, 1))
assert "the 250 guards" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/oqs-copy/test/validate.py; then
  echo "ERROR: a date beside an OPEN question exempted a stale total — the shape that disarmed this guard once"
  exit 1
else
  echo "OK: validator correctly FAILs — an open question is a live claim whatever dates sit beside it"
fi
