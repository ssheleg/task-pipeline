#!/usr/bin/env bash
# name: Negative self-test (the same disarm, against the graph fixtures)
set -eu
rm -rf /tmp/b80g-copy && cp -R . /tmp/b80g-copy
python3 - <<'EOF'
p = "/tmp/b80g-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
start = t.index("def violations(")
end = t.index("\ndef ", start)
body = t[start:end]
needle = 'if n.get("status") != "parked":'
assert needle in body, "PLANT DID NOT LAND: b80g — the runtime rule moved"
open(p, "w", encoding="utf-8").write(
    t[:start] + body.replace(needle, "if False:", 1) + t[end:])
EOF
if python3 /tmp/b80g-copy/test/graph_test.py; then
  echo "ERROR: the B-080 fixtures passed against a graph.py that refuses nothing —
         fixtures nobody watched fail are decoration"; exit 1
else
  echo "OK: graph_test.py's own check fixtures bind"
fi
