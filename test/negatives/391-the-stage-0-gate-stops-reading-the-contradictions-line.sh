#!/usr/bin/env bash
# name: Negative self-test (the stage-0 gate stops reading the contradictions line)
set -eu
rm -rf /tmp/cx2-copy && cp -R . /tmp/cx2-copy
python3 - <<'EOF'
import re
p = "/tmp/cx2-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 0 — Intake grill.*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cx2 — no stage 0 section"
g = re.search(r"\n- \*\*GATE \((?:manual|auto)\).*?(?=\n\S|\Z)", m.group(0), re.S)
assert g, "PLANT DID NOT LAND: cx2 — no GATE bullet"
_g = re.sub(r"(?i)contradictions:", "notes:", g.group(0))
assert _g != g.group(0), "PLANT DID NOT LAND: cx2 — the gate never named it"
sec = m.group(0)[:g.start()] + _g + m.group(0)[g.end():]
open(p, "w", encoding="utf-8").write(t[:m.start()] + sec + t[m.end():])
EOF
if python3 /tmp/cx2-copy/test/validate.py 2>&1 | grep -q "does not read the ledger"; then
  echo "OK: validator FAILs — a check the gate does not require is one a run skips"
else
  echo "ERROR: the gate can drop the criterion while the prose keeps it"
  exit 1
fi
