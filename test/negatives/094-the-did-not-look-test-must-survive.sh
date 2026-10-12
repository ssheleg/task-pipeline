#!/usr/bin/env bash
# name: Negative self-test (the did-not-look test must survive)
set -eu
rm -rf /tmp/fs03-copy && cp -R . /tmp/fs03-copy
python3 - <<'EOF'
p = "/tmp/fs03-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
assert 'what does it print when it did not look' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('what does it print when it did not look', 'what does it print')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs03-copy/test/validate.py; then
  echo "ERROR: validator passed with the did-not-look test must survive broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the did-not-look test must survive"
fi
