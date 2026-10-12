#!/usr/bin/env bash
# name: Negative self-test (the worktree-per-agent rule is removed)
set -eu
rm -rf /tmp/ag1-copy && cp -R . /tmp/ag1-copy
python3 - <<'EOF'
p = "/tmp/ag1-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
n = '**A worktree per agent, always.**'
assert n in t, "PLANT DID NOT LAND: ag1"
_planted = t.replace(n, '**Try to avoid overlapping.**', 1)
assert _planted != t, "PLANT DID NOT LAND: ag1"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ag1-copy/test/validate.py 2>&1 | grep -q 'worktree rule is gone'; then
  echo "OK: validator FAILs — sharing a checkout is what corrupts two independent changes into one state"
else
  echo "ERROR: two agents may share a working tree again, which cost four version collisions in one session"
  exit 1
fi
