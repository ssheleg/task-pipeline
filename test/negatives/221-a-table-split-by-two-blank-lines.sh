#!/usr/bin/env bash
# name: Negative self-test (a table split by TWO blank lines)
set -eu
rm -rf /tmp/tbl2-copy && cp -R . /tmp/tbl2-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): pinned to `| B-015 |` this plant lands only
# while that row is open — a row closing moves it into the Closed list
# and the split would be planted into prose, or nowhere. Any row of the
# live table splits it, so take the last one, which is unambiguously
# inside the table rather than against its header.
import re
p = "/tmp/tbl2-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
rows = re.findall(r"^\| B-\d+[a-z]? \|", t, re.M)
assert rows, "PLANT DID NOT LAND: the board holds no rows to split"
needle = rows[-1]
open(p, "w", encoding="utf-8").write(t.replace(needle, "\n\n" + needle, 1))
EOF
if python3 /tmp/tbl2-copy/test/validate.py; then
  echo "ERROR: two blank lines end a table exactly like one, and the guard saw neither"
  exit 1
else
  echo "OK: validator correctly FAILs — the gap is any length, because GFM ends the table at the first blank"
fi
