#!/usr/bin/env bash
# name: Negative self-test (the verifier told to read a field again by name only)
set -eu
rm -rf /tmp/b80h-copy && cp -R . /tmp/b80h-copy
python3 - <<'EOF'
p = "/tmp/b80h-copy/plugins/task-pipeline/agents/verifier.md"
t = open(p, encoding="utf-8").read()
needle = "**Run the node's `check`.**"
assert needle in t, "PLANT DID NOT LAND: b80h — the doctrine no longer names the field"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "**Run the checks the task named.**", 1))
EOF
if python3 /tmp/b80h-copy/test/validate.py; then
  echo "ERROR: doctrine naming no field was accepted — B-080 is exactly that
         sentence, and nothing compared it against the schema for a day"; exit 1
else
  echo "OK: what the verifier is told to read is compared against what the node has"
fi
