#!/usr/bin/env bash
# name: Negative self-test (prose in the Human column)
set -eu
rm -rf /tmp/vf2-copy && cp -R . /tmp/vf2-copy
python3 - <<'EOF'
p = "/tmp/vf2-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
needle = "| pass | never | — |"
assert needle in t, "PLANT DID NOT LAND: anchor absent before the edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "| pass | soon | — |", 1))
EOF
if python3 /tmp/vf2-copy/test/validate.py; then
  echo "ERROR: 'soon' in the one column a machine may not fill — the question stops being answerable"
  exit 1
else
  echo "OK: validator correctly FAILs — a date or the literal never, nothing else"
fi
