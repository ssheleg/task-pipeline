#!/usr/bin/env bash
# name: Negative self-test (a default stage route points at a sibling)
set -eu
rm -rf /tmp/fw07-route-copy && cp -R . /tmp/fw07-route-copy
python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, '/tmp/fw07-route-copy/test')
from stage_routes import DETAILS
p = Path('/tmp/fw07-route-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md')
s = p.read_text()
a = f'[{DETAILS[0]}]({DETAILS[0]})'
b = f'[{DETAILS[1]}]({DETAILS[1]})'
assert s.count(a) == 1, 'PLANT DID NOT LAND: exact intake route'
p.write_text(s.replace(a, b))
PY
set +e
out=$(python3 /tmp/fw07-route-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -q 'stage routes: stage 0 needs its one exact'; then
  echo 'OK: validator rejects a sibling detail on the actual default-stage route'
else
  echo "$out"
  echo 'ERROR: wrong-stage route did not produce its intended refusal'
  exit 1
fi
