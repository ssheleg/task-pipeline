#!/usr/bin/env bash
# name: Negative self-test (the REQ spine must stay in the brief template)
set -eu
rm -rf /tmp/req-copy && cp -R . /tmp/req-copy
python3 - <<'EOF'
import re
p = "/tmp/req-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(re.sub(r"^## Requirements.*", "## Notes", t, flags=re.M))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: the-req-spine-must-stay-in-the-brief"
EOF
if python3 /tmp/req-copy/test/validate.py; then
  echo "ERROR: validator passed a brief template with no REQ spine"
  exit 1
else
  echo "OK: validator requires the REQ spine in the brief template"
fi
