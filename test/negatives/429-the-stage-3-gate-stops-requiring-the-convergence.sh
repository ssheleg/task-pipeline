#!/usr/bin/env bash
# name: Negative self-test (the stage-3 gate stops requiring the convergence)
set -eu
rm -rf /tmp/cx5-copy && cp -R . /tmp/cx5-copy
python3 - <<'EOF'
import re
p = "/tmp/cx5-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 3 — Spec.*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cx5 — no stage 3 section"
g = re.search(r"\n- \*\*GATE \(manual\).*?(?=\n\S|\Z)", m.group(0), re.S)
assert g, "PLANT DID NOT LAND: cx5 — no GATE bullet"
_g = re.sub(r"(?i)converge\w*", "combine", g.group(0))
assert _g != g.group(0), "PLANT DID NOT LAND: cx5 — the gate never named it"
sec = m.group(0)[:g.start()] + _g + m.group(0)[g.end():]
# The prose lives in the stage-3 detail the validator reads beside the spine.
_detail = open("/tmp/cx5-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-03-spec.md", encoding="utf-8").read()
assert "converge" in _detail, "PLANT OVERREACHED: the prose must survive"
open(p, "w", encoding="utf-8").write(t[:m.start()] + sec + t[m.end():])
EOF
if python3 /tmp/cx5-copy/test/validate.py 2>&1 | grep -q "GATE does not require the tracks"; then
  echo "OK: validator FAILs — the criterion would live only in prose"
else
  echo "ERROR: the gate can drop it while the prose keeps it"
  exit 1
fi
