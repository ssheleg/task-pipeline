#!/usr/bin/env bash
# name: Negative self-test (stages.md drops the worktree fan-out precondition)
set -eu
rm -rf /tmp/cv6-copy && cp -R . /tmp/cv6-copy
python3 - <<'EOF'
import re
p = "/tmp/cv6-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^## 5 — Dev.*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: cv6 — no stage 5 section"
_sec = re.sub(r"(?i)worktree", "workspace", m.group(0))
assert _sec != m.group(0), "PLANT DID NOT LAND: cv6 — stage 5 never named it"
open(p, "w", encoding="utf-8").write(t[:m.start()] + _sec + t[m.end():])
EOF
if python3 /tmp/cv6-copy/test/validate.py 2>&1 | grep -q "drops the worktree"; then
  echo "OK: validator FAILs — one working tree with two writers is corrupted state"
else
  echo "ERROR: the condition that was never missing is the one nothing guards"
  exit 1
fi
