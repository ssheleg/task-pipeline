#!/usr/bin/env bash
# name: Negative self-test (an open row homed in a scratchpad must fail)
set -eu
rm -rf /tmp/prk2-copy && cp -R . /tmp/prk2-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): which template row is open is a property of the
# template, not a constant — the seeded example is edited whenever the
# board's own columns move. Take whichever row is open.
import re
p = "/tmp/prk2-copy/plugins/task-pipeline/skills/task-pipeline/templates/backlog.md"
t = open(p, encoding="utf-8").read()
line = [l for l in t.splitlines()
        if re.match(r"^\|\s*B-\d+\s*\|", l)
        and len(l.split("|")) > 3 and l.split("|")[-3].strip() == "open"]
assert line, "PLANT DID NOT LAND: the template holds no open row"
cells = line[0].split("|")
cells[-3] = " open — held at scratchpad/b29/ "
open(p, "w", encoding="utf-8").write(t.replace(line[0], "|".join(cells), 1))
EOF
if python3 /tmp/prk2-copy/test/validate.py 2>&1 | grep -q "per-session directory"; then
  echo "OK: validator FAILs — a scratchpad is not a home"
else
  echo "ERROR: work can be homed somewhere nothing keeps it"
  exit 1
fi
