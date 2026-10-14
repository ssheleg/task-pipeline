#!/usr/bin/env bash
# name: Negative self-test (continuity calls completion a search that ran dry)
set -eu
rm -rf /tmp/fl7-continuity-copy && cp -R . /tmp/fl7-continuity-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl7-continuity-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md')
s = p.read_text()
old = 'completion — the iteration\'s finish line\nreached ([`finish-line.md`](finish-line.md)), never a search that ran dry.'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the continuity completion citation'
p.write_text(s.replace(old, 'completion.'))
PY
set +e
out=$(python3 /tmp/fl7-continuity-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF "FL-G7: references/continuity.md's 'It stops for exactly four things'"; then
  echo "OK: validator FAILs — continuity's completion cites the finish line"
else
  echo "$out"
  echo 'ERROR: completion lost its finish line and nothing objected'
  exit 1
fi
