#!/usr/bin/env bash
# name: Negative self-test (an open ledger row with no board id)
set -eu
rm -rf /tmp/bd1-copy && cp -R . /tmp/bd1-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): which id a carry-over row points at is a fact
# about that ledger, not a constant — the rows were renumbered once
# already. Take the first pointer the file actually carries.
import re
p = "/tmp/bd1-copy/docs/evidence/specs/2026-08-08-audit-followup-carryover.md"
t = open(p, encoding="utf-8").read()
# A WELL-FORMED row, chosen by shape: this ledger holds two rows whose cell
# count differs from its header, and those belong to the sibling plant below
# that probes the FALLBACK path. Three plants derived from "the first
# `B-\d+` in the file" collapsed onto one row and left two guard branches
# unprobed — the independent reader found it by replaying both trees.
_rows = [l for l in t.splitlines() if l.strip().startswith("|")
         and "---" not in l]
assert _rows, "PLANT DID NOT LAND: the ledger has no table"
_w = len(_rows[0].split("|"))
m = next((mm for l in _rows[1:] if len(l.split("|")) == _w
          for mm in re.finditer(r" → `B-\d+`", l)), None)
assert m, "PLANT DID NOT LAND: no well-formed row carries a board pointer"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "", 1))
assert m.group(0) not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/bd1-copy/test/validate.py; then
  echo "ERROR: an open row with no board id passed — the dangling pointer the board exists to resolve"
  exit 1
else
  echo "OK: validator correctly FAILs — every open ledger row names a board id"
fi
