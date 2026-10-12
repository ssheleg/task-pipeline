#!/usr/bin/env bash
# name: Negative self-test (a collision warning inside the frontier rows)
set -eu
rm -rf /tmp/col1-copy && cp -R . /tmp/col1-copy
python3 - <<'EOF'
p = "/tmp/col1-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = '              "is what they touch", file=sys.stderr)'
assert needle in t, "PLANT DID NOT LAND: col1 — the collision print moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, '              "is what they touch")', 1))
EOF
if python3 /tmp/col1-copy/test/validate.py; then
  echo "ERROR: a collision warning printed among the frontier rows was accepted —
         B-093: those rows are parsed one per node and paid for on every iteration
         of every loop, so a warning among them reads as a node"; exit 1
else
  echo "OK: next is run and its two streams are checked separately"
fi
