#!/usr/bin/env bash
# name: Negative self-test (the rubric keeps the Effect verification item)
set -eu
rm -rf /tmp/fs13-copy && cp -R . /tmp/fs13-copy
python3 - <<'EOF'
p = "/tmp/fs13-copy/plugins/task-pipeline/skills/task-pipeline/references/review.md"
t = open(p, encoding="utf-8").read()
assert '**Effect verification.**' in t, "PLANT DID NOT LAND: needle absent before edit"
t = t.replace('**Effect verification.**', '**Vibes check.**')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs13-copy/test/validate.py; then
  echo "ERROR: validator passed with the rubric keeps the Effect verification item broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the rubric keeps the Effect verification item"
fi
