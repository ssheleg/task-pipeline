#!/usr/bin/env bash
# name: Negative self-test (waves.py base_repro values drift from the inventory schema)
set -eu
rm -rf /tmp/fl4b-enum-copy && cp -R . /tmp/fl4b-enum-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl4b-enum-copy/plugins/task-pipeline/skills/task-pipeline/scripts/waves.py')
s = p.read_text()
old = 'BASE_REPRO = ("yes", "no", "n/a")'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the BASE_REPRO constant'
p.write_text(s.replace(old, 'BASE_REPRO = ("yes", "no", "unknown")'))
PY
set +e
out=$(python3 /tmp/fl4b-enum-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF 'FL-G4: scripts/waves.py BASE_REPRO'; then
  echo 'OK: validator FAILs — the hand enums in waves.py equal inventory/1 enums'
else
  echo "$out"
  echo 'ERROR: waves.py base_repro drifted from the schema and nothing objected'
  exit 1
fi
