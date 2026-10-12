#!/usr/bin/env bash
# name: Negative self-test (a board row too short to compute a priority)
set -eu
rm -rf /tmp/bd10-copy && cp -R . /tmp/bd10-copy
python3 - <<'EOF'
# DERIVED anchor (B-113), and this one is aimed at the LIVE board: pinned
# to `| B-008 |` the plant stops landing the day that row closes, which is
# the release doing its job. Take whatever row the board holds, and keep
# its id so the truncation is the only defect planted.
import re
p = "/tmp/bd10-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
row = [l for l in t.splitlines() if re.match(r"^\| B-\d+[a-z]? \|", l)]
assert row, "PLANT DID NOT LAND: the board holds no rows"
rid = row[0].split("|")[1].strip()
open(p, "w", encoding="utf-8").write(
    t.replace(row[0], "| %s | short | src | S | 999 |" % rid, 1))
EOF
if python3 /tmp/bd10-copy/test/validate.py; then
  echo "ERROR: a malformed row was skipped in silence, carrying any priority it liked"
  exit 1
else
  echo "OK: validator correctly FAILs — a row it cannot compute is reported, not skipped"
fi
