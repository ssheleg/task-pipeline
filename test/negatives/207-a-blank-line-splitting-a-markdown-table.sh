#!/usr/bin/env bash
# name: Negative self-test (a blank line splitting a markdown table)
set -eu
rm -rf /tmp/tbl-copy && cp -R . /tmp/tbl-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): pinned to `| B-015 |` this plant lands only
# while that row is open — a row closing moves it into the Closed list
# and the split would be planted into prose, or nowhere. Any row of the
# live table splits it, so take the last one, which is unambiguously
# inside the table rather than against its header.
import re
p = "/tmp/tbl-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
rows = re.findall(r"^\| B-\d+[a-z]? \|", t, re.M)
assert rows, "PLANT DID NOT LAND: the board holds no rows to split"
needle = rows[-1]
open(p, "w", encoding="utf-8").write(t.replace(needle, "\n" + needle, 1))
EOF
if python3 /tmp/tbl-copy/test/validate.py; then
  echo "ERROR: a split table passed — every row below the gap renders as prose, silently"
  exit 1
else
  echo "OK: validator correctly FAILs — the class that hit this repo's own board is now a check"
fi
