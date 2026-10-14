#!/usr/bin/env bash
# name: Negative self-test (the hand-back stops saying why the iteration stopped)
set -eu
rm -rf /tmp/fl6-handback-copy && cp -R . /tmp/fl6-handback-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl6-handback-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md')
s = p.read_text()
old = 'FINISH      finish: done | budget | blocked'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the hand-back FINISH field'
p.write_text(s.replace(old, 'FINISH      whatever the run felt like'))
PY
set +e
out=$(python3 /tmp/fl6-handback-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF 'FL-G6: references/progress.md → The hand-back has no'; then
  echo 'OK: validator FAILs — the hand-back carries the finish word'
else
  echo "$out"
  echo 'ERROR: the hand-back lost its finish word and nothing objected'
  exit 1
fi
