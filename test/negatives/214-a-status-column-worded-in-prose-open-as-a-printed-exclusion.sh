#!/usr/bin/env bash
# name: Negative self-test (a status column worded in prose — "open as a printed exclusion")
set -eu
rm -rf /tmp/bd12-copy && cp -R . /tmp/bd12-copy
python3 - <<'EOF'
p = "/tmp/bd12-copy/docs/evidence/specs/2026-08-09-prose-carryover.md"
open(p, "w", encoding="utf-8").write(
    "# Carry-over — scratch\n\n"
    "| # | Stage | What | Why it isn't done | REQ | Where it lives now |\n"
    "|---|---|---|---|---|---|\n"
    "| 1 | 5 Dev | a thing | later | — | open as a printed exclusion |\n")
EOF
if python3 /tmp/bd12-copy/test/validate.py; then
  echo "ERROR: a status column saying 'open …' in prose was not read as open — this repo has live rows worded that way"
  exit 1
else
  echo "OK: validator correctly FAILs — inside a status column, a word boundary is enough"
fi
