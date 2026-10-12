#!/usr/bin/env bash
# name: Negative self-test (an unverified effect must stay Important)
set -eu
rm -rf /tmp/fs14-copy && cp -R . /tmp/fs14-copy
python3 - <<'EOF'
p = "/tmp/fs14-copy/plugins/task-pipeline/skills/task-pipeline/references/review.md"
t = open(p, encoding="utf-8").read()
assert 'unverified claim, and it is **Important**' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('unverified claim, and it is **Important**', 'unverified claim, and it is **Minor**')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs14-copy/test/validate.py; then
  echo "ERROR: validator passed with an unverified effect must stay Important broken"
  exit 1
else
  echo "OK: validator correctly FAILs — an unverified effect must stay Important"
fi
