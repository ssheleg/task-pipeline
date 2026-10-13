#!/usr/bin/env bash
# name: Negative self-test (stages.md drops the same-group fan-out precondition)
set -eu
rm -rf /tmp/cv5-copy && cp -R . /tmp/cv5-copy
python3 - <<'EOF'
import re
p = "/tmp/cv5-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-05-dev.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 5 — Dev.*?(?=^## |\Z)", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv5 — no stage 5 section"
_sec = re.sub(r"(?i)depends|same group", "run together", m.group(0))
assert _sec != m.group(0), "PLANT DID NOT LAND: cv5 — stage 5 never named it"
open(p, "w", encoding="utf-8").write(t[:m.start()] + _sec + t[m.end():])
EOF
if python3 /tmp/cv5-copy/test/validate.py 2>&1 | grep -q "drops the same-group"; then
  echo "OK: validator FAILs — two tasks with a dependency are not a parallel group however exclusive their files"
else
  echo "ERROR: one of the three preconditions can drop again, in the other direction"
  exit 1
fi
