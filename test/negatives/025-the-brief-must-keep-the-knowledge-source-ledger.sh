#!/usr/bin/env bash
# name: Negative self-test (the brief must keep the knowledge-source ledger)
set -eu
rm -rf /tmp/ledger-copy && cp -R . /tmp/ledger-copy
python3 - <<'EOF'
import re
p = "/tmp/ledger-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(re.sub(r"^## Knowledge sources.*", "## Notes", t, flags=re.M))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: the-brief-must-keep-the-knowledge-so"
EOF
if python3 /tmp/ledger-copy/test/validate.py; then
  echo "ERROR: validator passed a brief template with nowhere to record the harvest"
  exit 1
else
  echo "OK: validator requires the stage-0 source ledger in the brief template"
fi
