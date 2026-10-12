#!/usr/bin/env bash
# name: Negative self-test (the report must require verified-by lines)
set -eu
rm -rf /tmp/fs10-copy && cp -R . /tmp/fs10-copy
python3 - <<'EOF'
p = "/tmp/fs10-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
assert '`verified-by:` line' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('`verified-by:` line', '`looks-fine:` line')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs10-copy/test/validate.py; then
  echo "ERROR: validator passed with the report must require verified-by lines broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the report must require verified-by lines"
fi
