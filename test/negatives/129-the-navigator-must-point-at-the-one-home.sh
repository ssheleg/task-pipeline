#!/usr/bin/env bash
# name: Negative self-test (the navigator must point at the one home)
set -eu
rm -rf /tmp/ed3-copy && cp -R . /tmp/ed3-copy
python3 - <<'EOF'
p = "/tmp/ed3-copy/plugins/task-pipeline/skills/evidence-docs/SKILL.md"
t = open(p, encoding="utf-8").read()
assert 'documentation.md) → *The canons*' in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace('documentation.md) → *The canons*', 'documentation.md)'))
EOF
if python3 /tmp/ed3-copy/test/validate.py; then
  echo "ERROR: validator passed with the navigator must point at the one home broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the navigator must point at the one home"
fi
