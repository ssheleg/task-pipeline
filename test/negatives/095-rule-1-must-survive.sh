#!/usr/bin/env bash
# name: Negative self-test (rule 1 must survive)
set -eu
rm -rf /tmp/fs04-copy && cp -R . /tmp/fs04-copy
python3 - <<'EOF'
p = "/tmp/fs04-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
assert 'Verify by re-reading, not by the reply' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('Verify by re-reading, not by the reply', 'Verify carefully')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs04-copy/test/validate.py; then
  echo "ERROR: validator passed with rule 1 must survive broken"
  exit 1
else
  echo "OK: validator correctly FAILs — rule 1 must survive"
fi
