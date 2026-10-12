#!/usr/bin/env bash
# name: Negative self-test (the canon/rule boundary must stay stated)
set -eu
rm -rf /tmp/cn4-copy && cp -R . /tmp/cn4-copy
python3 - <<'EOF'
p = "/tmp/cn4-copy/plugins/task-pipeline/skills/task-pipeline/references/documentation.md"
t = open(p, encoding="utf-8").read()
assert 'epistemic' in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace('epistemic', 'vibes-based'))
EOF
if python3 /tmp/cn4-copy/test/validate.py; then
  echo "ERROR: validator passed with the canon/rule boundary must stay stated broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the canon/rule boundary must stay stated"
fi
