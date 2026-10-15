#!/usr/bin/env bash
# name: Negative self-test (waves.py learns a triage class the doctrine does not know)
set -eu
rm -rf /tmp/fl4-vocab-copy && cp -R . /tmp/fl4-vocab-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl4-vocab-copy/plugins/task-pipeline/skills/task-pipeline/scripts/waves.py')
s = p.read_text()
old = 'TRIAGE = ("blocking", "deferred", "noise")'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the waves.py TRIAGE constant'
p.write_text(s.replace(old, 'TRIAGE = ("blocking", "deferred", "ignored")'))
PY
set +e
out=$(python3 /tmp/fl4-vocab-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF 'FL-G4: scripts/waves.py carries classes'; then
  echo 'OK: validator FAILs — one triage vocabulary on every surface'
else
  echo "$out"
  echo 'ERROR: waves.py drifted from the triage vocabulary and nothing objected'
  exit 1
fi
