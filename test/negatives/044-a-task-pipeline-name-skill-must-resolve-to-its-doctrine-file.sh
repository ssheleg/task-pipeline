#!/usr/bin/env bash
# name: Negative self-test (a task-pipeline:<name> skill must resolve to its doctrine file)
set -eu
rm -rf /tmp/doctrine-ptr-copy && cp -R . /tmp/doctrine-ptr-copy
python3 - <<'EOF'
p = "/tmp/doctrine-ptr-copy/plugins/task-pipeline/skills/task-pipeline/pipeline.example.json"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(
    t.replace('"task-pipeline:grill"', '"task-pipeline:interrogation"'))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-task-pipeline-name-skill-must-reso"
EOF
if python3 /tmp/doctrine-ptr-copy/test/validate.py; then
  echo "ERROR: validator passed a stage pointed at doctrine that does not exist"
  exit 1
else
  echo "OK: validator requires every task-pipeline:<name> to resolve to references/<name>.md"
fi
