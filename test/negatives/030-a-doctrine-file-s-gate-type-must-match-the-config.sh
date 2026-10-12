#!/usr/bin/env bash
# name: Negative self-test (a doctrine file's gate type must match the config)
set -eu
rm -rf /tmp/doctrinegate-copy && cp -R . /tmp/doctrinegate-copy
python3 - <<'EOF'
import re
p = "/tmp/doctrinegate-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(re.sub(r"^## GATE \(manual\)", "## GATE (auto)", t, flags=re.M))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-doctrine-file-s-gate-type-must-mat"
EOF
if python3 /tmp/doctrinegate-copy/test/validate.py; then
  echo "ERROR: validator passed a doctrine gate type contradicting pipeline.example.json"
  exit 1
else
  echo "OK: validator keeps each stage doctrine's gate type in sync with the config"
fi
