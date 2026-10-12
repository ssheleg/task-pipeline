#!/usr/bin/env bash
# name: Negative self-test (a standing instruction must carry its retirement trigger)
set -eu
rm -rf /tmp/retro-prune-copy && cp -R . /tmp/retro-prune-copy
python3 - <<'EOF'
p = "/tmp/retro-prune-copy/plugins/task-pipeline/skills/task-pipeline/templates/retro.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace("Retire when", "Notes"))
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-standing-instruction-must-carry-it"
EOF
if python3 /tmp/retro-prune-copy/test/validate.py; then
  echo "ERROR: validator passed a retro template with no retirement trigger — the prune becomes an argument and the list grows until nobody reads it"
  exit 1
else
  echo "OK: validator requires every standing instruction to carry its retire-when trigger"
fi
