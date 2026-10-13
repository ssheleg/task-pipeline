#!/usr/bin/env bash
# name: Negative self-test (stages.md drops the convergence check from its stage-5 summary)
set -eu
rm -rf /tmp/cv3-copy && cp -R . /tmp/cv3-copy
python3 - <<'EOF'
import re
p = "/tmp/cv3-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-05-dev.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 5 — Dev.*?(?=^## |\Z)", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv3 — no stage 5 section"
_sec = m.group(0).replace("convergence check", "review")
assert _sec != m.group(0), "PLANT DID NOT LAND: cv3 — stage 5 never named it"
_planted = t[:m.start()] + _sec + t[m.end():]
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/cv3-copy/test/validate.py 2>&1 | grep -q "never mentions the group"; then
  echo "OK: validator FAILs — a summary that drops the rule is how two surfaces disagreed about fan-out"
else
  echo "ERROR: the summary can drift from build.md again, unwatched"
  exit 1
fi
