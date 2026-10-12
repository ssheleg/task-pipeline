#!/usr/bin/env bash
# name: Negative self-test (the Carries column is dropped from the plan template)
set -eu
rm -rf /tmp/fe2-copy && cp -R . /tmp/fe2-copy
python3 - <<'EOF'
import re
p = "/tmp/fe2-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
_planted = re.sub(r"[Cc]arries", "notes", t)
assert _planted != t, "PLANT DID NOT LAND: fe2"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fe2-copy/test/validate.py 2>&1 | grep -q "no .Carries. column"; then
  echo "OK: validator FAILs — without the column, an unfillable payload is invisible to a reviewer"
else
  echo "ERROR: the column that mechanises the fake-edge test can vanish silently"
  exit 1
fi
