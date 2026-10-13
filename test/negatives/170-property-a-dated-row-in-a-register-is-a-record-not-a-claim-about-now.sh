#!/usr/bin/env bash
# name: Property check (a DATED row in a register is a record, not a claim about now)
set -eu
rm -rf /tmp/cr5d-copy && cp -R . /tmp/cr5d-copy
python3 - <<'EOF'
# The board and the retro exist to say what was true on a day. Correcting those
# numbers would rewrite the record, so a number inside a dated item is exempt —
# and that exemption is what let the registers into the corpus at all.
p = "/tmp/cr5d-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
anchor = "| id | What | Source | Size | Sev | Blast | Age | Prio | State | Home |"
separator = "|---|---|---|---|---|---|---|---|---|---|"
anchor += "\n" + separator
assert anchor in t, "PLANT DID NOT LAND: complete table header absent before edit"
row = ("| B-000 | Measured 2026-08-11: the bundle held 32 reference files. | audit, "
       "2026-08-11 | S | 1 | 1 | 0 | **1** | **closed 2026-08-11** — record only. | \u2014 |")
t = t.replace(anchor, anchor + "\n" + row, 1)
open(p, "w", encoding="utf-8").write(t)
assert "32 reference files" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/cr5d-copy/test/validate.py; then
  echo "OK: validator correctly PASSES — a dated board row is a measurement of its date"
else
  echo "ERROR: the registry refused a dated record; the board cannot record what was true"
  exit 1
fi
