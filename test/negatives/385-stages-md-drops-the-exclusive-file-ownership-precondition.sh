#!/usr/bin/env bash
# name: Negative self-test (stages.md drops the exclusive-file-ownership precondition)
set -eu
rm -rf /tmp/cv8-copy && cp -R . /tmp/cv8-copy
python3 - <<'EOF'
import re
p = "/tmp/cv8-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-05-dev.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 5 — Dev.*?(?=^## |\Z)", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv8 — no stage 5 section"
_sec = re.sub(r"(?i)exclusive|file ownership", "separate", m.group(0))
assert _sec != m.group(0), "PLANT DID NOT LAND: cv8 — stage 5 never named it"
open(p, "w", encoding="utf-8").write(t[:m.start()] + _sec + t[m.end():])
EOF
if python3 /tmp/cv8-copy/test/validate.py 2>&1 | grep -q "drops exclusive file"; then
  echo "OK: validator FAILs — the precondition F-5 was actually about is guarded in its own direction"
else
  echo "ERROR: the branch that found F-5 is the one branch with no plant behind it"
  exit 1
fi
