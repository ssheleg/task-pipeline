#!/usr/bin/env bash
# name: Negative self-test (a board row with no Source — the reverse direction)
set -eu
rm -rf /tmp/bd3-copy && cp -R . /tmp/bd3-copy
python3 - <<'EOF'
import re
p = "/tmp/bd3-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
# DERIVED, not a literal id: this probe named B-009 and broke the day that row
# closed. A needle that has to be maintained goes stale between the change and
# the run — B-057's own class, caught loudly by negatives.py rather than silently.
m = next((x for x in re.finditer(r"^\| (B-\d+\w*) \|([^|]*)\|([^|]*)\|", t, re.M)
          if x.group(3).strip()), None)
assert m, "PLANT DID NOT LAND: no open board row carries a Source"
open(p, "w", encoding="utf-8").write(t[:m.start(3)] + " " + t[m.end(3):])
EOF
if python3 /tmp/bd3-copy/test/validate.py; then
  echo "ERROR: a board row traceable to nothing passed — a gap has one side and so does an invention"
  exit 1
else
  echo "OK: validator correctly FAILs — both directions are checked"
fi
