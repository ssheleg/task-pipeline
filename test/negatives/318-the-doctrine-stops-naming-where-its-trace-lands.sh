#!/usr/bin/env bash
# name: Negative self-test (the doctrine stops naming where its trace lands)
set -eu
rm -rf /tmp/hb08-copy && cp -R . /tmp/hb08-copy
python3 - <<'EOF'
p = "/tmp/hb08-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
n = "as a `hand:` line"
assert n in t, "PLANT DID NOT LAND: hb08"
# Every mention, not the first: the section names the shape twice, and removing
# one left the guard reading the other.
open(p, "w", encoding="utf-8").write(t.replace(n, "somewhere durable", -1).replace("`hand:`", "the trace", -1))
EOF
if python3 /tmp/hb08-copy/test/validate.py 2>&1 | grep -q 'never names the ledger line its trace lands on'; then
  echo "OK: validator FAILs — a narrative with no address is one no audit can find"
else
  echo "ERROR: the doctrine lost the address and nothing objected"
  exit 1
fi
