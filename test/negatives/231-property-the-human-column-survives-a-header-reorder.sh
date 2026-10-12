#!/usr/bin/env bash
# name: Property check (the Human column survives a header reorder)
set -eu
rm -rf /tmp/hr-copy && cp -R . /tmp/hr-copy
python3 - <<'EOF'
import re
p = "/tmp/hr-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
old = "| REQ | What | Run | Shipped in | Observed at | Environment | Auto | Human | Note |"
assert old in t, "PLANT DID NOT LAND: header absent"
t = t.replace(old, "| REQ | What | Run | Shipped in | Observed at | Environment | Auto | Note | Human |")
# Any Auto value, not just `pass`: four rows read `none` after a review round,
# and a plant that skips them leaves half the table in the old column order.
#
# And any NOTE value, not just `—` — the identical failure one column over, found
# on 2026-08-15 when seven rows carrying an audit's finding ids (`F-1`, `F-5 · F-6`)
# went unmatched, stayed in the old order under a reordered header, and made this
# check report the doctrine broken when the plant was what had gone narrow. A plant
# anchored on the CONTENT of a cell describes the table it was written against.
t = re.sub(r"\| (pass|none|partial) \| (never|\d{4}-\d{2}-\d{2}) \| ([^|\n]*) \|",
           r"| \1 | \3 | \2 |", t)
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/hr-copy/test/validate.py >/dev/null; then
  echo "OK: the column is found by name, so moving it does not silently misread a neighbour"
else
  echo "ERROR: reordering the header broke the check — it was reading a position, not a column"
  exit 1
fi
