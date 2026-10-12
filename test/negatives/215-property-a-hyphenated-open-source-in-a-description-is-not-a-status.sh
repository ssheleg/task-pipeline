#!/usr/bin/env bash
# name: Property check (a hyphenated "Open-source" in a description is not a status)
set -eu
rm -rf /tmp/hyp-copy && cp -R . /tmp/hyp-copy
python3 - <<'EOF'
p = "/tmp/hyp-copy/docs/evidence/specs/2026-08-09-hyphen-carryover.md"
open(p, "w", encoding="utf-8").write(
    "# Carry-over — scratch\n\n"
    "| # | Stage | What | Why it isn't done | REQ | Where it lives now |\n"
    "|---|---|---|---|---|---|\n"
    "| 1 | 5 Dev | Open-source license text is missing | done | — | closed |\n")
EOF
if python3 /tmp/hyp-copy/test/validate.py >/dev/null; then
  echo "OK: the What column is never read as a status, so punctuation in prose cannot fake one"
else
  echo "ERROR: a closed row was flagged because its description began 'Open-source'"
  exit 1
fi
