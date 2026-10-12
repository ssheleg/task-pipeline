#!/usr/bin/env bash
# name: Negative self-test (prose in Human, rescued by a date in Note)
set -eu
rm -rf /tmp/vf5-copy && cp -R . /tmp/vf5-copy
python3 - <<'EOF'
p = "/tmp/vf5-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
needle = "| pass | never | — |"
assert needle in t, "PLANT DID NOT LAND: anchor absent before the edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "| pass | soon | 2026-08-09 |", 1))
EOF
if python3 /tmp/vf5-copy/test/validate.py; then
  echo "ERROR: a bare date in Note satisfied a row whose Human said 'soon' — the one thing this guard rejects"
  exit 1
else
  echo "OK: validator correctly FAILs — the Human column is located by name, not by scanning every cell"
fi
