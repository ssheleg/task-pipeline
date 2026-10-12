#!/usr/bin/env bash
# name: Negative self-test (the hand-back loses its trace in the ledger)
set -eu
rm -rf /tmp/hb07-copy && cp -R . /tmp/hb07-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the `<N|10>` placeholder carries the review cap,
# a number the doctrine has already moved once — the plant is about the
# LINE existing, so match its shape.
import re
p = "/tmp/hb07-copy/plugins/task-pipeline/skills/task-pipeline/templates/run.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"(?m)^hand:\s+<N\|\d+>", t)
assert m, "PLANT DID NOT LAND: hb07"
i = m.start(); j = t.index("\n", i)
open(p, "w", encoding="utf-8").write(t[:i] + t[j+1:])
EOF
if python3 /tmp/hb07-copy/test/validate.py 2>&1 | grep -q 'no .hand:. line shape'; then
  echo "OK: validator FAILs — a gate criterion with no trace is 'copy it, tick it' one level up"
else
  echo "ERROR: the ledger lost the hand: shape and the gate kept requiring the report"
  exit 1
fi
