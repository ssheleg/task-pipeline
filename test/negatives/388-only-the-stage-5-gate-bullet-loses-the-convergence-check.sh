#!/usr/bin/env bash
# name: Negative self-test (only the stage-5 GATE bullet loses the convergence check)
set -eu
rm -rf /tmp/cv11-copy && cp -R . /tmp/cv11-copy
python3 - <<'EOF'
import re
p = "/tmp/cv11-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 5 — Dev.*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv11 — no stage 5 section"
sec = m.group(0)
# Strip it from the GATE bullet ONLY. cv3 removes it everywhere and would pass on
# the whole-section check alone, which leaves the GATE-bullet branch unproven —
# the narrative bullet (now in stage-05-dev.md) is deliberately left intact so only
# that branch can fire.
g = re.search(r"\n- \*\*GATE \(auto\).*?(?=\n\S|\Z)", sec, re.S)
assert g, "PLANT DID NOT LAND: cv11 — no GATE bullet in stage 5"
_g = g.group(0).replace("convergence check", "per-task review")
assert _g != g.group(0), "PLANT DID NOT LAND: cv11 — the GATE bullet never named it"
_sec = sec[:g.start()] + _g + sec[g.end():]
# The narrative lives in the stage-5 detail the validator reads beside the spine;
# the plant touches only the spine, so that copy must still name the check.
_detail = open("/tmp/cv11-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-05-dev.md", encoding="utf-8").read()
assert "convergence check" in _detail, "PLANT OVERREACHED: the narrative bullet must survive"
open(p, "w", encoding="utf-8").write(t[:m.start()] + _sec + t[m.end():])
EOF
if python3 /tmp/cv11-copy/test/validate.py 2>&1 | grep -q "GATE bullet does not require"; then
  echo "OK: validator FAILs on the GATE-bullet branch specifically, with the narrative bullet still present"
else
  echo "ERROR: the GATE-bullet branch is unproven — cv3 passes it via the whole-section check"
  exit 1
fi
