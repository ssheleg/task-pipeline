#!/usr/bin/env bash
# name: Negative self-test (REQ rows must name how they are verified)
set -eu
rm -rf /tmp/verify-copy && cp -R . /tmp/verify-copy
python3 - <<'EOF'
p = "/tmp/verify-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace("How it's verified", "Notes"))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: req-rows-must-name-how-they-are-veri"
EOF
if python3 /tmp/verify-copy/test/validate.py; then
  echo "ERROR: validator passed a REQ table with no verification column"
  exit 1
else
  echo "OK: validator requires a named check per requirement"
fi
