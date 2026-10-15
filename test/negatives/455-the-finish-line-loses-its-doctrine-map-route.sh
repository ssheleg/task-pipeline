#!/usr/bin/env bash
# name: Negative self-test (the finish line loses its doctrine-map route)
set -eu
rm -rf /tmp/fl1-route-copy && cp -R . /tmp/fl1-route-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl1-route-copy/plugins/task-pipeline/skills/task-pipeline/references/doctrine-map.md')
s = p.read_text()
old = '| `references/finish-line.md` |'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the doctrine-map row'
p.write_text(s.replace(old, '| `references/loop-guard.md` (was finish-line) |'))
PY
set +e
out=$(python3 /tmp/fl1-route-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF 'FL-G1: references/doctrine-map.md has no row'; then
  echo 'OK: validator FAILs — the finish line must stay routed from the doctrine map'
else
  echo "$out"
  echo 'ERROR: the finish line lost its route and nothing objected'
  exit 1
fi
