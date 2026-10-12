#!/usr/bin/env bash
# name: Negative self-test (validator must be able to fail)
set -eu
rm -rf /tmp/corrupt-copy && cp -R . /tmp/corrupt-copy
# corrupt the version so marketplace/plugin/CHANGELOG drift
python3 - <<'EOF'
import re
p = "/tmp/corrupt-copy/plugins/task-pipeline/.claude-plugin/plugin.json"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(
    re.sub(r'"version": "[0-9.]*"', '"version": "0.0.0-corrupt"', t))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: validator-must-be-able-to-fail"
EOF
if python3 /tmp/corrupt-copy/test/validate.py; then
  echo "ERROR: validator passed on a corrupted copy — it cannot fail"
  exit 1
else
  echo "OK: validator correctly FAILs on corrupted copy"
fi
