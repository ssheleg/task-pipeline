#!/usr/bin/env bash
# name: Negative self-test (brief template must keep the autonomy sweep)
set -eu
rm -rf /tmp/brief-copy && cp -R . /tmp/brief-copy
python3 - <<'EOF'
import re
p = "/tmp/brief-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(re.sub(r"^## Autonomy.*", "## Notes", t, flags=re.M))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: brief-template-must-keep-the-autonom"
EOF
if python3 /tmp/brief-copy/test/validate.py; then
  echo "ERROR: validator passed a brief template with no autonomy sweep"
  exit 1
else
  echo "OK: validator requires the autonomy sweep in the brief template"
fi
