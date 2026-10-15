#!/usr/bin/env bash
# name: Negative self-test (the brief template carries another release budget)
set -eu
rm -rf /tmp/fl3-budget-copy && cp -R . /tmp/fl3-budget-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl3-budget-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md')
s = p.read_text()
old = '`maxReleases` 2'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the release budget in the brief'
p.write_text(s.replace(old, '`maxReleases` 4'))
PY
set +e
out=$(python3 /tmp/fl3-budget-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF 'FL-G3: the default maxReleases disagrees'; then
  echo 'OK: validator FAILs — the default budgets agree on all three surfaces'
else
  echo "$out"
  echo 'ERROR: two release budgets shipped and nothing objected'
  exit 1
fi
