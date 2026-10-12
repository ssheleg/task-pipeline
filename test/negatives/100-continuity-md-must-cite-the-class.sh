#!/usr/bin/env bash
# name: Negative self-test (continuity.md must cite the class)
set -eu
rm -rf /tmp/fs09-copy && cp -R . /tmp/fs09-copy
python3 - <<'EOF'
p = "/tmp/fs09-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
assert '*False success*' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('*False success*', '*that other thing*')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs09-copy/test/validate.py; then
  echo "ERROR: validator passed with continuity.md must cite the class broken"
  exit 1
else
  echo "OK: validator correctly FAILs — continuity.md must cite the class"
fi
