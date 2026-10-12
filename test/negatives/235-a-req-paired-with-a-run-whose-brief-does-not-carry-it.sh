#!/usr/bin/env bash
# name: Negative self-test (a REQ paired with a run whose brief does not carry it)
set -eu
rm -rf /tmp/wr-copy && cp -R . /tmp/wr-copy
python3 - <<'EOF'
p = "/tmp/wr-copy/docs/evidence/verification.md"
_orig_bytes = open(p, "rb").read()
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(
    t + "| REQ-014 | wrong pairing | `2026-08-04-run-continuity` | v1.10.0 | — | pass | never | — |\n")
assert open(p, "rb").read() != _orig_bytes, "PLANT DID NOT LAND: a-req-paired-with-a-run-whose-brief"
EOF
if python3 /tmp/wr-copy/test/validate.py; then
  echo "ERROR: ids 001-014 recur across every brief, so a union check passes almost any mispairing"
  exit 1
else
  echo "OK: validator correctly FAILs — the REQ is checked against the brief the row NAMES"
fi
