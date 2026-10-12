#!/usr/bin/env bash
# name: Negative self-test (a ledger pointing at a board id nobody issued)
set -eu
rm -rf /tmp/bd2-copy && cp -R . /tmp/bd2-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): any issued id will do — what is under test is a
# pointer at an id nobody issued, not the id `B-001` in particular, and
# that row has already been renumbered once in this ledger's life.
import re
p = "/tmp/bd2-copy/docs/evidence/specs/2026-08-08-audit-followup-carryover.md"
t = open(p, encoding="utf-8").read()
# A WELL-FORMED row: the dangling-id check has two branches and the
# mismatched-shape row belongs to the sibling plant below. Derived from
# "the first `B-\d+`" this plant and that one performed byte-identical
# mutations and one guard branch went unprobed.
_rows = [l for l in t.splitlines() if l.strip().startswith("|")
         and "---" not in l]
assert _rows, "PLANT DID NOT LAND: the ledger has no table"
_w = len(_rows[0].split("|"))
m = next((mm for l in _rows[1:] if len(l.split("|")) == _w
          for mm in re.finditer(r"B-\d+", l)), None)
assert m, "PLANT DID NOT LAND: no well-formed row names a board id"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "B-999", 1))
assert "B-999" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/bd2-copy/test/validate.py; then
  echo "ERROR: a pointer to an id nobody issued reads as filed and is not"
  exit 1
else
  echo "OK: validator correctly FAILs — the id has to exist on the board"
fi
