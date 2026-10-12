#!/usr/bin/env bash
# name: Negative self-test (build.md's GATE stops requiring the convergence check)
set -eu
rm -rf /tmp/cv7-copy && cp -R . /tmp/cv7-copy
python3 - <<'EOF'
import re
p = "/tmp/cv7-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## GATE \(auto\).*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv7 — no GATE section"
_sec = re.sub(r"(?i)convergence", "review", m.group(0))
assert _sec != m.group(0), "PLANT DID NOT LAND: cv7 — the GATE never required it"
open(p, "w", encoding="utf-8").write(t[:m.start()] + _sec + t[m.end():])
EOF
if python3 /tmp/cv7-copy/test/validate.py 2>&1 | grep -q "described in .4.2a and not required by the gate"; then
  echo "OK: validator FAILs — a criterion that lives only in prose is one a run can skip"
else
  echo "ERROR: the gate can drop the criterion while the prose still describes it"
  exit 1
fi
