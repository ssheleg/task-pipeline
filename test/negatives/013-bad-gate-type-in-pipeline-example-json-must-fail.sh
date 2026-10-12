#!/usr/bin/env bash
# name: Negative self-test (bad gate type in pipeline.example.json must fail)
set -eu
rm -rf /tmp/gate-copy && cp -R . /tmp/gate-copy
python3 - <<'EOF'
p = "/tmp/gate-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace('"type": "auto"', '"type": "sometimes"'))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: bad-gate-type-in-pipeline-example-js"
EOF
if python3 /tmp/gate-copy/test/validate.py; then
  echo "ERROR: validator passed an invalid gate.type"
  exit 1
else
  echo "OK: validator rejects an invalid gate.type"
fi
