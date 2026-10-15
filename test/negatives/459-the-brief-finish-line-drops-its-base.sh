#!/usr/bin/env bash
# name: Negative self-test (the brief's finish line drops its base)
set -eu
rm -rf /tmp/fl5-base-copy && cp -R . /tmp/fl5-base-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl5-base-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md')
s = p.read_text()
old = '- **Base:** <the commit this iteration started from>\n'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the Base field of the brief'
p.write_text(s.replace(old, ''))
PY
set +e
out=$(python3 /tmp/fl5-base-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF "FL-G5: templates/brief.md's \`## Finish line\` lacks ['Base']"; then
  echo "OK: validator FAILs — the brief's finish line carries all five fields"
else
  echo "$out"
  echo 'ERROR: the finish line lost its base and nothing objected'
  exit 1
fi
