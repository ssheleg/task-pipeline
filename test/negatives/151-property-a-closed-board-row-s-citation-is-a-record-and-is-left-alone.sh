#!/usr/bin/env bash
# name: Property check (a CLOSED board row's citation is a record and is left alone)
set -eu
rm -rf /tmp/cite3-copy && cp -R . /tmp/cite3-copy
python3 - <<'EOF'
# B-081 is closed and cites `references/knowledge-graph.md:100-129` with no needle.
# It was current at closing; demanding a rewrite would edit the record.
p = "/tmp/cite3-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
assert "`references/knowledge-graph.md:100-129`" in t, "PLANT DID NOT LAND: the closed row's citation is gone"
EOF
if python3 /tmp/cite3-copy/test/validate.py >/dev/null; then
  echo "OK: a closed row's citation is a record, not a live claim"
else
  echo "ERROR: the currency check reached into closed rows, where every citation would need rewriting"
  exit 1
fi
