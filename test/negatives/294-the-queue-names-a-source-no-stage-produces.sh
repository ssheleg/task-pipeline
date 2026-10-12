#!/usr/bin/env bash
# name: Negative self-test (the queue names a source no stage produces)
set -eu
rm -rf /tmp/lp04-copy && cp -R . /tmp/lp04-copy
python3 - <<'EOF'
p = "/tmp/lp04-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
t = open(p, encoding="utf-8").read()
n = '"module-map"'
assert n in t, "PLANT DID NOT LAND: lp04"
open(p, "w", encoding="utf-8").write(t.replace(n, '"whatever-is-next"', 1))
EOF
if python3 /tmp/lp04-copy/test/validate.py 2>&1 | grep -q 'does not offer .module-map'; then
  echo "OK: validator FAILs — the queue must name a list this pipeline actually builds"
else
  echo "ERROR: the queue named a source nothing produces and nothing objected"
  exit 1
fi
