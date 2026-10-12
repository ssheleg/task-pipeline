#!/usr/bin/env bash
# name: Negative self-test (a ledger row with no `Environment` cell)
set -eu
rm -rf /tmp/env1-copy && cp -R . /tmp/env1-copy
python3 - <<'EOF'
# B-099: `Observed at` says which tree the check saw; nothing said where it RAN, so
# a smoke test against a preview URL entered the record indistinguishable from one
# against production. A row that omits the question is refused; `—` is an answer.
p = "/tmp/env1-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read().splitlines(True)
hit = next(i for i, l in enumerate(t) if l.startswith("| REQ-"))
cells = t[hit].split("|")
assert len(cells) == 11, "PLANT DID NOT LAND: the row is not the shape this plant expects"
del cells[6]
t[hit] = "|".join(cells)
open(p, "w", encoding="utf-8").write("".join(t))
assert len(open(p, encoding="utf-8").read().splitlines()[hit].split("|")) == 10, "PLANT DID NOT LAND"
EOF
if python3 /tmp/env1-copy/test/validate.py; then
  echo "ERROR: validator passed a verification row with no Environment cell"
  exit 1
else
  echo "OK: validator correctly FAILs — every evidence row records where it ran"
fi
