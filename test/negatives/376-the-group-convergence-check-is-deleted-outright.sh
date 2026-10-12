#!/usr/bin/env bash
# name: Negative self-test (the group convergence check is deleted outright)
set -eu
rm -rf /tmp/cv1-copy && cp -R . /tmp/cv1-copy
python3 - <<'EOF'
import re
p = "/tmp/cv1-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^### 4\.2a The group convergence check.*?(?=^#{2,3} )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv1 — no 4.2a section"
_planted = t[:m.start()] + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND: cv1"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/cv1-copy/test/validate.py 2>&1 | grep -q "no group convergence check"; then
  echo "OK: validator FAILs — a fanned-out group would integrate with no cross-diff check"
else
  echo "ERROR: the whole convergence rule can be removed and only its phrases were guarded"
  exit 1
fi
