#!/usr/bin/env bash
# name: Negative self-test (a restated fixture count that disagrees with the fixture file)
set -eu
rm -rf /tmp/anc4-copy && cp -R . /tmp/anc4-copy
python3 - <<'EOF'
# The loop guard tripped on B-113's own closure line: the same sentence in the
# same file returned twice with the same stale fixture count, inside the
# paragraph that narrates a stale count as the row's lesson. Each fix appended
# a corrected sentence instead of correcting the one already there, so the old
# one survived every round. Canon 8 ends it — the count is computed now, and
# this plant is what keeps it computed.
#
# DERIVED: read whatever the corpus states and move it, so the plant cannot go
# stale the way the sentence it guards did.
import re
p = "/tmp/anc4-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"(\d+) whole-workflow fixtures", t)
assert m, "PLANT DID NOT LAND: the closure line states no fixture count"
skewed = "%d whole-workflow fixtures" % (int(m.group(1)) + 6)
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), skewed, 1))
assert skewed in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/anc4-copy/test/validate.py 2>&1 | grep -q "anchor-census fixtures computes to"; then
  echo "OK: validator FAILs — the fixture count is computed from the fixture file, so the fifth occurrence is a failing gate rather than a reader's patience"
else
  echo "ERROR: a restated fixture count disagreed with the file and nothing objected — the class that recurred four times inside its own fix"
  exit 1
fi
