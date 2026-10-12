#!/usr/bin/env bash
# name: Negative self-test (a ledger row whose cell count does not match its header)
set -eu
rm -rf /tmp/b80i-copy && cp -R . /tmp/b80i-copy
python3 - <<'EOF'
p = "/tmp/b80i-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read()
# The real defect, put back: an unescaped `|` inside a cell. CI found it on
# 2026-08-19 and every local gate run had passed, because with the shipped
# column order the extra cells landed to the RIGHT of `Human`.
needle = "`test/negatives.py` filtered on receipt, record and containers"
assert needle in t, "PLANT DID NOT LAND: b80i — the note no longer reads as expected"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "`test/negatives.py -k receipt|record|containers`", 1))
EOF
if python3 /tmp/b80i-copy/test/validate.py; then
  echo "ERROR: a row with more cells than its header was accepted — every column
         after the pipe is then read one out, and Human was still green"; exit 1
else
  echo "OK: a row that does not line up with its header is refused"
fi
