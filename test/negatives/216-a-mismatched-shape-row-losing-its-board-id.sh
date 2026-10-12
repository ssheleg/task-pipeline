#!/usr/bin/env bash
# name: Negative self-test (a mismatched-shape row losing its board id)
set -eu
rm -rf /tmp/bd13-copy && cp -R . /tmp/bd13-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the row under test is the one whose cell count
# differs from its header, and which id it carries is incidental — the
# ledger has been renumbered once already.
import re
p = "/tmp/bd13-copy/docs/evidence/specs/2026-08-08-audit-followup-carryover.md"
t = open(p, encoding="utf-8").read()
# THE MISMATCHED ROW, derived by the property under test: this plant exists
# because a row whose cell count differs from its header was skipped before
# the id check ran, and taking "the first `B-\d+` in the file" made it the
# same mutation as the sibling plant above — true only until a row is
# inserted, and by then neither branch is probed.
_rows = [l for l in t.splitlines() if l.strip().startswith("|")
         and "---" not in l]
assert _rows, "PLANT DID NOT LAND: the ledger has no table"
_w = len(_rows[0].split("|"))
m = next((mm for l in _rows[1:] if len(l.split("|")) != _w
          for mm in re.finditer(r"B-\d+", l)), None)
assert m, "PLANT DID NOT LAND: no row's cell count differs from its header"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "B-999", 1))
EOF
if python3 /tmp/bd13-copy/test/validate.py; then
  echo "ERROR: a row whose cell count differs from its header was skipped before the id check ran"
  exit 1
else
  echo "OK: validator correctly FAILs — the fallback matches on a word boundary, not exact equality"
fi
