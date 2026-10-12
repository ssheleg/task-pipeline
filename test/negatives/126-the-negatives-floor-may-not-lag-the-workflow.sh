#!/usr/bin/env bash
# name: Negative self-test (the negatives floor may not lag the workflow)
set -eu
rm -rf /tmp/ci06-copy && cp -R . /tmp/ci06-copy
python3 - <<'EOF'
import re
p = "/tmp/ci06-copy/test/negatives.py"
t = open(p, encoding="utf-8").read()
m = re.search(r"^MIN_EXPECTED\s*=\s*(\d+)", t, re.M)
assert m, "PLANT DID NOT LAND: MIN_EXPECTED not found"
lowered = int(m.group(1)) - 4
open(p, "w", encoding="utf-8").write(
    t.replace(m.group(0), f"MIN_EXPECTED = {lowered}", 1))
EOF
if python3 /tmp/ci06-copy/test/validate.py; then
  echo "ERROR: validator passed with the negatives floor lagging the workflow"
  exit 1
else
  echo "OK: validator correctly FAILs — the negatives floor may not lag the workflow"
fi
