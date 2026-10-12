#!/usr/bin/env bash
# name: Negative self-test (the hygiene gate must name its blind side)
set -eu
rm -rf /tmp/fs12-copy && cp -R . /tmp/fs12-copy
python3 - <<'EOF'
p = "/tmp/fs12-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
assert 'cannot see what the task did' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('cannot see what the task did', 'sees everything')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs12-copy/test/validate.py; then
  echo "ERROR: validator passed with the hygiene gate must name its blind side broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the hygiene gate must name its blind side"
fi
