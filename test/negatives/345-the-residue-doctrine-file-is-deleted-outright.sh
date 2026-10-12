#!/usr/bin/env bash
# name: Negative self-test (the residue doctrine file is deleted outright)
set -eu
rm -rf /tmp/res13-copy && cp -R . /tmp/res13-copy
python3 - <<'EOF'
import os, re
p = "/tmp/res13-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
assert os.path.isfile(p), "PLANT DID NOT LAND: res13"
os.remove(p)
assert not os.path.exists(p), "PLANT DID NOT LAND: res13"
EOF
if python3 /tmp/res13-copy/test/validate.py 2>&1 | grep -q 'references/residue.md is gone'; then
  echo "OK: validator FAILs — every gate prints holds: and the doctrine behind it must exist"
else
  echo "ERROR: the file defining eight classes and the teardown vanished and the suite stayed green"
  exit 1
fi
