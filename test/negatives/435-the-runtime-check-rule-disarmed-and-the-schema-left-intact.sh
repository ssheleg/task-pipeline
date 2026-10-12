#!/usr/bin/env bash
# name: Negative self-test (the runtime check rule disarmed, and the schema left intact)
set -eu
rm -rf /tmp/b80f-copy && cp -R . /tmp/b80f-copy
python3 - <<'EOF'
p = "/tmp/b80f-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
# Anchored INSIDE violations(): the schema is never applied to a LIVE graph, so a
# rule stated only in the format is a rule the run does not have.
start = t.index("def violations(")
end = t.index("\ndef ", start)
body = t[start:end]
needle = 'if n.get("status") != "parked":'
assert needle in body, "PLANT DID NOT LAND: b80f — the runtime rule moved"
open(p, "w", encoding="utf-8").write(
    t[:start] + body.replace(needle, "if False:", 1) + t[end:])
EOF
if python3 /tmp/b80f-copy/test/validate.py; then
  echo "ERROR: the run stopped refusing a node with no completion test while the
         schema still stated the rule — the split that has disagreed three times"; exit 1
else
  echo "OK: validate.py RUNS the script over a planted graph, not only the format"
fi
