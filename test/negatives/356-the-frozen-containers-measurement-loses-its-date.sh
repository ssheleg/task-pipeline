#!/usr/bin/env bash
# name: Negative self-test (the frozen containers measurement loses its date)
set -eu
rm -rf /tmp/res24-copy && cp -R . /tmp/res24-copy
python3 - <<'EOF'
p = "/tmp/res24-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
# DERIVED anchor (B-113): a re-measurement re-dates this line, and the
# plant pinned to the old date would land nowhere while reporting green.
import re
m = re.search(r"Measured \d{4}-\d\d-\d\d, enumerating", t)
assert m, "PLANT DID NOT LAND: res24"
_planted = t.replace(m.group(0), "Measured recently, enumerating", 1)
assert _planted != t, "PLANT DID NOT LAND: res24"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res24-copy/test/validate.py 2>&1 | grep -q "lost its date"; then
  echo "OK: validator FAILs — an undated measurement reads as a claim about now"
else
  echo "ERROR: a frozen measurement lost its date and nothing noticed"
  exit 1
fi
