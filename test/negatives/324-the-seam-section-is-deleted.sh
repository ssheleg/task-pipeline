#!/usr/bin/env bash
# name: Negative self-test (the seam section is deleted)
set -eu
rm -rf /tmp/ri06-copy && cp -R . /tmp/ri06-copy
python3 - <<'EOF'
p = "/tmp/ri06-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = '## A seam is not a deliverable'
assert n in t, "PLANT DID NOT LAND: ri06"
_planted = t.replace(n, '## Boundaries', 1)
assert _planted != t, "PLANT DID NOT LAND: ri06"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri06-copy/test/validate.py 2>&1 | grep -q 'no section on the seam'; then
  echo "OK: validator FAILs — two green halves reporting a working whole"
else
  echo "ERROR: the rule went missing and nothing objected — two green halves reporting a working whole"
  exit 1
fi
