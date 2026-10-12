#!/usr/bin/env bash
# name: Negative self-test (the not-torn-down section is deleted, not merely reworded)
set -eu
rm -rf /tmp/res14-copy && cp -R . /tmp/res14-copy
python3 - <<'EOF'
import os, re
p = "/tmp/res14-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## What must \*\*not\*\* be torn down.*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: res14"
_planted = t[:m.start()] + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND: res14"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res14-copy/test/validate.py 2>&1 | grep -q 'no section on what must not be torn down'; then
  echo "OK: validator FAILs — the section is required to exist, not merely to be quoted elsewhere"
else
  echo "ERROR: the asymmetry section was removed wholesale and only its citations remained"
  exit 1
fi
