#!/usr/bin/env bash
# name: Negative self-test (the owner table loses its earlier-run row)
set -eu
rm -rf /tmp/res16-copy && cp -R . /tmp/res16-copy
python3 - <<'EOF'
import os, re
p = "/tmp/res16-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^\|\s*\*\*an earlier run of this project\*\*.*$", t, re.M)
assert m, "PLANT DID NOT LAND: res16"
_planted = t[:m.start()] + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND: res16"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res16-copy/test/validate.py 2>&1 | grep -q 'lost its `an earlier run'; then
  echo "OK: validator FAILs — the state that says which debris a run may clear must exist"
else
  echo "ERROR: the middle owner state disappeared and the two remaining ones read as complete"
  exit 1
fi
