#!/usr/bin/env bash
# name: Negative self-test (the False success law must be stated)
set -eu
rm -rf /tmp/fs02-copy && cp -R . /tmp/fs02-copy
python3 - <<'EOF'
p = "/tmp/fs02-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
assert 're-reading the state it changed' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('re-reading the state it changed', 'asking again politely')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs02-copy/test/validate.py; then
  echo "ERROR: validator passed with the False success law must be stated broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the False success law must be stated"
fi
