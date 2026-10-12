#!/usr/bin/env bash
# name: Negative self-test (the self-pacing mode is withdrawn)
set -eu
rm -rf /tmp/lp03-copy && cp -R . /tmp/lp03-copy
python3 - <<'EOF'
p = "/tmp/lp03-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
t = open(p, encoding="utf-8").read()
n = '"dynamic"'
assert n in t, "PLANT DID NOT LAND: lp03"
open(p, "w", encoding="utf-8").write(t.replace(n, '"paced"', 1))
EOF
if python3 /tmp/lp03-copy/test/validate.py 2>&1 | grep -q 'has no .dynamic'; then
  echo "OK: validator FAILs — a self-pacing run needs a way to record that it is one"
else
  echo "ERROR: dynamic left the enum and nothing objected"
  exit 1
fi
