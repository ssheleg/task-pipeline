#!/usr/bin/env bash
# name: Negative self-test (an invariant may not claim a guard that does not exist)
set -eu
rm -rf /tmp/inv-copy && cp -R . /tmp/inv-copy
python3 - <<'EOF'
p = "/tmp/inv-copy/CONTRIBUTING.md"
t = open(p, encoding="utf-8").read()
old = "(guard: `manifest names`)"
assert old in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace(old, "(guard: `a check nobody wrote`)", 1))
EOF
if python3 /tmp/inv-copy/test/validate.py; then
  echo "ERROR: validator passed an invariant list claiming an enforcement that does not exist — the list says it IS what the validator enforces"
  exit 1
else
  echo "OK: every cited invariant names a guard this validator actually prints"
fi
