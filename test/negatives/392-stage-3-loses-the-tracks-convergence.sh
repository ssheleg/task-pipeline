#!/usr/bin/env bash
# name: Negative self-test (stage 3 loses the tracks convergence)
set -eu
rm -rf /tmp/cx3-copy && cp -R . /tmp/cx3-copy
python3 - <<'EOF'
import re
p = "/tmp/cx3-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-03-spec.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 3 — Spec.*?(?=^## |\Z)", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cx3 — no stage 3 section"
sec = re.sub(r"(?i)converge\w*", "combine", m.group(0))
assert sec != m.group(0), "PLANT DID NOT LAND: cx3 — stage 3 never named it"
open(p, "w", encoding="utf-8").write(t[:m.start()] + sec + t[m.end():])
EOF
if python3 /tmp/cx3-copy/test/validate.py 2>&1 | grep -q "without their convergence"; then
  echo "OK: validator FAILs — each track is right alone and they disagree together"
else
  echo "ERROR: the two tracks can converge on one screen unchecked"
  exit 1
fi
