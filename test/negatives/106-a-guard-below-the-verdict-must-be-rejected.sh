#!/usr/bin/env bash
# name: Negative self-test (a guard below the verdict must be rejected)
set -eu
rm -rf /tmp/fs15-copy && cp -R . /tmp/fs15-copy
python3 - <<'EOF'
p = "/tmp/fs15-copy/test/validate.py"
t = open(p, encoding="utf-8").read()
needle = 'print("PASS: task-pipeline structure valid")'
assert needle in t, "PLANT DID NOT LAND: verdict line absent"
t = t.replace(needle, needle + '\nfail("a check that can never run")')
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/fs15-copy/test/validate.py; then
  echo "ERROR: validator passed with a guard below the verdict"
  exit 1
else
  echo "OK: validator correctly FAILs — a guard below the verdict"
fi
