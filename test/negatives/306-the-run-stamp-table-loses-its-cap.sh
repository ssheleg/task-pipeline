#!/usr/bin/env bash
# name: Negative self-test (the run-stamp table loses its cap)
set -eu
rm -rf /tmp/rs01-copy && cp -R . /tmp/rs01-copy
python3 - <<'EOF'
import re
p = "/tmp/rs01-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
# DERIVED: find the row the guard finds, then remove the cap from the segment
# that names the stamps. The first version held the cell verbatim and would
# have died red on a cosmetic reflow.
out, done = [], False
for l in t.splitlines(True):
    if not done and l.startswith("|") and "retro.md" in l.lower() and "run stamps" in l.lower():
        i = l.lower().index("run stamps")
        j = l.find("|", i)
        seg = l[i:j if j > 0 else len(l)]
        seg2 = re.sub(r"\(max[^)]*\)", "(one line each)", seg, count=1)
        assert seg2 != seg, "PLANT DID NOT LAND: rs01 — the stamps segment states no cap"
        l = l[:i] + seg2 + (l[j:] if j > 0 else "")
        done = True
    out.append(l)
assert done, "PLANT DID NOT LAND: rs01 — no row naming retro.md's run stamps"
open(p, "w", encoding="utf-8").write("".join(out))
EOF
if python3 /tmp/rs01-copy/test/validate.py 2>&1 | grep -q "run stamps are given no cap"; then
  echo "OK: validator FAILs — one line per run is a slope, not a bound"
else
  echo "ERROR: the stamp table lost its cap and the section read in full kept growing"
  exit 1
fi
