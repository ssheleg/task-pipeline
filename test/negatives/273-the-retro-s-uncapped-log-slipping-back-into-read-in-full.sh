#!/usr/bin/env bash
# name: Negative self-test (the retro's uncapped log slipping back into "read in full")
set -eu
rm -rf /tmp/rf1-copy && cp -R . /tmp/rf1-copy
python3 - <<'EOF'
p = "/tmp/rf1-copy/docs/evidence/retro.md"
t = open(p, encoding="utf-8").read()
n = "The **Recent log** and the **archive**"
assert n in t, "PLANT DID NOT LAND: the read-in-full sentence moved"
open(p, "w", encoding="utf-8").write(
    t.replace(n, "The **Recent log** is read in full. The **archive**", 1))
EOF
if python3 /tmp/rf1-copy/test/validate.py; then
  echo "ERROR: an uncapped section is back inside the source whose cap justifies reading it"
  exit 1
else
  echo "OK: validator correctly FAILs — the narrative log is queried, not read"
fi
