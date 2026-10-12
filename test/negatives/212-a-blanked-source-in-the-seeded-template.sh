#!/usr/bin/env bash
# name: Negative self-test (a blanked Source in the seeded template)
set -eu
rm -rf /tmp/bd11-copy && cp -R . /tmp/bd11-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): which id the template's first row carries is a
# property of the template. Take whichever row still states a Source.
import re
p = "/tmp/bd11-copy/plugins/task-pipeline/skills/task-pipeline/templates/backlog.md"
t = open(p, encoding="utf-8").read()
m = next((mm for mm in re.finditer(r"(?m)^\| B-\d+ \|([^|]*)\|([^|]*)\|", t)
          if mm.group(2).strip()), None)
assert m, "PLANT DID NOT LAND: no template row states a Source"
open(p, "w", encoding="utf-8").write(t[:m.start(2)] + " " + t[m.end(2):])
EOF
if python3 /tmp/bd11-copy/test/validate.py; then
  echo "ERROR: the reverse check covered this repo's board and not the file seeded into every host project"
  exit 1
else
  echo "OK: validator correctly FAILs — both boards, like the arithmetic check beside it"
fi
