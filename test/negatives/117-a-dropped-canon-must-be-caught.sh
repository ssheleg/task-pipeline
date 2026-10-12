#!/usr/bin/env bash
# name: Negative self-test (a dropped canon must be caught)
set -eu
rm -rf /tmp/cn2-copy && cp -R . /tmp/cn2-copy
python3 - <<'EOF'
p = "/tmp/cn2-copy/plugins/task-pipeline/skills/task-pipeline/references/documentation.md"
t = open(p, encoding="utf-8").read()
assert '**7. Silence is not a pass.**' in t, "PLANT DID NOT LAND: needle absent before edit"
open(p, "w", encoding="utf-8").write(t.replace('**7. Silence is not a pass.**', '**7. Something vague.**'))
EOF
if python3 /tmp/cn2-copy/test/validate.py; then
  echo "ERROR: validator passed with a dropped canon must be caught broken"
  exit 1
else
  echo "OK: validator correctly FAILs — a dropped canon must be caught"
fi
