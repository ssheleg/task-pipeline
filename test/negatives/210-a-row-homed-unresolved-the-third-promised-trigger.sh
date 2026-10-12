#!/usr/bin/env bash
# name: Negative self-test (a row homed `unresolved` — the third promised trigger)
set -eu
rm -rf /tmp/bd9-copy && cp -R . /tmp/bd9-copy
python3 - <<'EOF'
p = "/tmp/bd9-copy/docs/evidence/specs/2026-08-09-scratch2-carryover.md"
open(p, "w", encoding="utf-8").write(
    "# Carry-over — scratch\n\n"
    "| # | Stage | What | Why it isn't done | REQ | Where it lives now |\n"
    "|---|---|---|---|---|---|\n"
    "| 1 | 5 Dev | a thing | later | — | unresolved |\n")
assert "unresolved |" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/bd9-copy/test/validate.py; then
  echo "ERROR: templates/carryover.md says unresolved blocks the stage-10 gate and it did not"
  exit 1
else
  echo "OK: validator correctly FAILs — all three not-done values are checked, not only the one the rows used"
fi
