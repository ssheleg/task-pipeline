#!/usr/bin/env bash
# name: Property check (a description beginning "Open" is not an open row)
set -eu
rm -rf /tmp/fp-copy && cp -R . /tmp/fp-copy
python3 - <<'EOF'
p = "/tmp/fp-copy/docs/evidence/specs/2026-08-09-scratch3-carryover.md"
open(p, "w", encoding="utf-8").write(
    "# Carry-over — scratch\n\n"
    "| # | Stage | What | Why it isn't done | REQ | Where it lives now |\n"
    "|---|---|---|---|---|---|\n"
    "| 1 | 5 Dev | Open source license text is missing from the bundle | done | — | closed |\n")
EOF
if python3 /tmp/fp-copy/test/validate.py >/dev/null; then
  echo "OK: a cell must BE a status, not merely begin with one — rule 10, a checker with false positives is worse than none"
else
  echo "ERROR: a closed row was reported as open because its description started with the word Open"
  exit 1
fi
