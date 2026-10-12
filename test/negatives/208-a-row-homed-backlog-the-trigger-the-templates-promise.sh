#!/usr/bin/env bash
# name: Negative self-test (a row homed `backlog` — the trigger the templates promise)
set -eu
rm -rf /tmp/bd8-copy && cp -R . /tmp/bd8-copy
python3 - <<'EOF'
p = "/tmp/bd8-copy/docs/evidence/specs/2026-08-09-scratch-carryover.md"
open(p, "w", encoding="utf-8").write(
    "# Carry-over — scratch\n\n"
    "| # | Stage | What | Why it isn't done | REQ | Where it lives now |\n"
    "|---|---|---|---|---|---|\n"
    "| 1 | 5 Dev | a thing | later | — | backlog |\n")
assert "backlog |" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/bd8-copy/test/validate.py; then
  echo "ERROR: the doctrine promised the gate refuses this shape and the gate did not"
  exit 1
else
  echo "OK: validator correctly FAILs — both triggers are enforced, not only the one the rows happened to use"
fi
