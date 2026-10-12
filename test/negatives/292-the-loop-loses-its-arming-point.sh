#!/usr/bin/env bash
# name: Negative self-test (the loop loses its arming point)
set -eu
rm -rf /tmp/lp02-copy && cp -R . /tmp/lp02-copy
python3 - <<'EOF'
p = "/tmp/lp02-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
t = open(p, encoding="utf-8").read()
n = '"arm": {'
assert n in t, "PLANT DID NOT LAND: lp02"
open(p, "w", encoding="utf-8").write(t.replace(n, '"arm_": {', 1))
EOF
if python3 /tmp/lp02-copy/test/validate.py 2>&1 | grep -q 'run.loop has no .arm'; then
  echo "OK: validator FAILs — arming at preflight arms a loop with nothing to walk"
else
  echo "ERROR: the arm field vanished and nothing objected"
  exit 1
fi
