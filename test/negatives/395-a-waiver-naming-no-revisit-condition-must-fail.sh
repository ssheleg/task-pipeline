#!/usr/bin/env bash
# name: Negative self-test (a waiver naming no revisit condition must fail)
set -eu
rm -rf /tmp/wv2-copy && cp -R . /tmp/wv2-copy
python3 - <<'EOF'
# DERIVED anchor (B-113), the sibling of the plant above and pinned the
# same way for the same invisible reason. What is under test is a waiver
# that names a revisit condition, so read the State cell.
import re
p = "/tmp/wv2-copy/plugins/task-pipeline/skills/task-pipeline/templates/backlog.md"
lines = open(p, encoding="utf-8").read().split("\n")
_t = next((n for n, ln in enumerate(lines)
           if re.match(r"^\|\s*B-\d+\s*\|", ln)
           and len(ln.split("|")) >= 11
           and "revisit:" in ln.split("|")[9]), None)
assert _t is not None, "PLANT DID NOT LAND: no waiver naming a revisit condition"
c = lines[_t].split("|")
c[9] = " waived "
lines[_t] = "|".join(c)
open(p, "w", encoding="utf-8").write("\n".join(lines))
EOF
if python3 /tmp/wv2-copy/test/validate.py 2>&1 | grep -q "names no .revisit:. condition"; then
  echo "OK: validator FAILs — a waiver with no trigger is never reconsidered"
else
  echo "ERROR: a decision can be recorded with nothing that would bring it back"
  exit 1
fi
