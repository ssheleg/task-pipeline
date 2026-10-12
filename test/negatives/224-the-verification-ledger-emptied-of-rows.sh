#!/usr/bin/env bash
# name: Negative self-test (the verification ledger emptied of rows)
set -eu
rm -rf /tmp/vf3-copy && cp -R . /tmp/vf3-copy
python3 - <<'EOF'
import re
p = "/tmp/vf3-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
assert re.search(r"^\| REQ-\d+ ", t, re.M), "PLANT DID NOT LAND: no rows before the edit"
open(p, "w", encoding="utf-8").write(re.sub(r"^\| REQ-\d+ .*$", "", t, flags=re.M))
EOF
if python3 /tmp/vf3-copy/test/validate.py; then
  echo "ERROR: an empty ledger reads exactly like a project that has shipped nothing"
  exit 1
else
  echo "OK: validator correctly FAILs — the plant lands in the file that DEFINES the ledger"
fi
