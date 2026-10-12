#!/usr/bin/env bash
# name: Negative self-test (an open row whose ledger has two status columns)
set -eu
rm -rf /tmp/bd7-copy && cp -R . /tmp/bd7-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the pointer this ledger carries is a fact about
# the ledger. Pinned to `B-015` the plant would stop landing the day that
# row is renumbered or the ledger is re-pointed.
import re
p = "/tmp/bd7-copy/docs/evidence/specs/2026-08-03-setup-and-autonomy-carryover.md"
t = open(p, encoding="utf-8").read()
m = re.search(r" → `B-\d+`", t)
assert m, "PLANT DID NOT LAND: the ledger carries no board pointer"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "", 1))
assert m.group(0) not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/bd7-copy/test/validate.py; then
  echo "ERROR: a ledger with both Status and Home hid an open row — five of ten ledgers here have that shape"
  exit 1
else
  echo "OK: validator correctly FAILs — the test is position-free, so a shape nobody anticipated cannot defeat it"
fi
