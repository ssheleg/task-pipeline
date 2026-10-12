#!/usr/bin/env bash
# name: Negative self-test (the run-stamp table grows past its cap)
set -eu
rm -rf /tmp/rs02-copy && cp -R . /tmp/rs02-copy
python3 - <<'EOF'
import re
v = open("/tmp/rs02-copy/test/validate.py", encoding="utf-8").read()
cap = int(re.search(r"^STAMP_CAP = (\d+)", v, re.M).group(1))
p = "/tmp/rs02-copy/docs/evidence/retro.md"
t = open(p, encoding="utf-8").read()
rows = re.findall(r"^[ \t]{0,3}\|\s*\d{4}-\d{2}-\d{2}\s*\|[^\n]*\n", t, re.M)
assert len(rows) == cap, "PLANT DID NOT LAND: rs02 — %d stamps, cap is %d" % (len(rows), cap)
# One more, in the shape the doctrine's own command appends — prose, not a row.
# A guard that counts table rows under one heading cannot see this at all.
i = t.index(rows[0])
open(p, "w", encoding="utf-8").write(t[:i] + "2026-08-11 · `deadbee`\n" + t[i:])
EOF
if python3 /tmp/rs02-copy/test/validate.py 2>&1 | grep -q "run stamps in a file read"; then
  echo "OK: validator FAILs — the eleventh stamp must rotate, in every shape the doctrine writes them"
else
  echo "ERROR: the file passed its cap inside a section read in full at stage 0"
  exit 1
fi
