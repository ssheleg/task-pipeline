#!/usr/bin/env bash
# name: Negative self-test (a stage-10 close-out rule must reach the surfaces that enforce it)
set -eu
rm -rf /tmp/closeout-copy && cp -R . /tmp/closeout-copy
python3 - <<'EOF'
import re
p = "/tmp/closeout-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(re.sub(r"submodule", "sub-module", t, flags=re.I))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-stage-10-close-out-rule-must-reach"
EOF
if python3 /tmp/closeout-copy/test/validate.py; then
  echo "ERROR: validator passed a close-out rule declared in SKILL.md but absent from the gate that enforces it"
  exit 1
else
  echo "OK: validator keeps the stage-10 close-out on every surface that defines it"
fi
