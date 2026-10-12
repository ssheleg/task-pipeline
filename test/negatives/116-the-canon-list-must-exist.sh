#!/usr/bin/env bash
# name: Negative self-test (the canon list must exist)
set -eu
rm -rf /tmp/cn1-copy && cp -R . /tmp/cn1-copy
python3 - <<'EOF'
p = "/tmp/cn1-copy/plugins/task-pipeline/skills/task-pipeline/references/documentation.md"
t = open(p, encoding="utf-8").read()
assert '## The canons' in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace('## The canons', '## Some notes'))
EOF
if python3 /tmp/cn1-copy/test/validate.py; then
  echo "ERROR: validator passed with the canon list must exist broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the canon list must exist"
fi
