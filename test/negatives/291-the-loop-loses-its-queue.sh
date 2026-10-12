#!/usr/bin/env bash
# name: Negative self-test (the loop loses its queue)
set -eu
rm -rf /tmp/lp01-copy && cp -R . /tmp/lp01-copy
python3 - <<'EOF'
p = "/tmp/lp01-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json"
t = open(p, encoding="utf-8").read()
n = '"queue": {'
assert n in t, "PLANT DID NOT LAND: lp01"
open(p, "w", encoding="utf-8").write(t.replace(n, '"queue_": {', 1))
EOF
if python3 /tmp/lp01-copy/test/validate.py 2>&1 | grep -q 'run.loop has no .queue'; then
  echo "OK: validator FAILs — a loop with no queue is a timer"
else
  echo "ERROR: the queue field vanished and an armed loop still picks by recollection"
  exit 1
fi
