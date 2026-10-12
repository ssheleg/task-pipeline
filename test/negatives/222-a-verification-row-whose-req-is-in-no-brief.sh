#!/usr/bin/env bash
# name: Negative self-test (a verification row whose REQ is in no brief)
set -eu
rm -rf /tmp/vf1-copy && cp -R . /tmp/vf1-copy
python3 - <<'EOF'
p = "/tmp/vf1-copy/docs/evidence/verification.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(
    t + "| REQ-999 | invented | `nowhere` | v1.0.0 | — | pass | never | — |\n")
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-verification-row-whose-req-is-in-n"
EOF
if python3 /tmp/vf1-copy/test/validate.py; then
  echo "ERROR: a ledger row about a requirement nobody wrote down passed"
  exit 1
else
  echo "OK: validator correctly FAILs — the reverse direction, a row about nothing"
fi
