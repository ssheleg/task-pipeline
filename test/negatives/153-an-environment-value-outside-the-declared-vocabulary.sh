#!/usr/bin/env bash
# name: Negative self-test (an `Environment` value outside the declared vocabulary)
set -eu
rm -rf /tmp/env2-copy && cp -R . /tmp/env2-copy
python3 - <<'EOF'
# An environment invented per row is a column nobody can compare two rows in. The
# vocabulary is read out of the shipped template, never listed in the checker.
p = "/tmp/env2-copy/docs/evidence/verification.md"
t = open(p, encoding="utf-8").read().splitlines(True)
hit = next(i for i, l in enumerate(t) if l.startswith("| REQ-"))
cells = t[hit].split("|")
assert cells[6].strip() == "—", "PLANT DID NOT LAND: cell 6 is not the Environment cell"
cells[6] = " staging-ish "
t[hit] = "|".join(cells)
open(p, "w", encoding="utf-8").write("".join(t))
assert "staging-ish" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/env2-copy/test/validate.py; then
  echo "ERROR: validator passed an Environment value the template never declares"
  exit 1
else
  echo "OK: validator correctly FAILs — the vocabulary is the template's, not the row's"
fi
