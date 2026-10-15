#!/usr/bin/env bash
# name: Negative self-test (a B2 entry drifts from the hotfix lane)
set -eu
rm -rf /tmp/fl2-hotfix-copy && cp -R . /tmp/fl2-hotfix-copy
python3 - <<'PY'
from pathlib import Path
p = Path('/tmp/fl2-hotfix-copy/plugins/task-pipeline/skills/task-pipeline/references/finish-line.md')
s = p.read_text()
old = '  - a credential has leaked\n'
assert s.count(old) == 1, 'PLANT DID NOT LAND: the B2 credential entry'
p.write_text(s.replace(old, '  - a credential might leak\n'))
PY
set +e
out=$(python3 /tmp/fl2-hotfix-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF 'FL-G2: finish-line.md'; then
  echo 'OK: validator FAILs — B2 and the hotfix lane are one computed set'
else
  echo "$out"
  echo 'ERROR: B2 drifted from the hotfix lane and nothing objected'
  exit 1
fi
