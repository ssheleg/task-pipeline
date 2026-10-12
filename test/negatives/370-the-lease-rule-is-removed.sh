#!/usr/bin/env bash
# name: Negative self-test (the lease rule is removed)
set -eu
rm -rf /tmp/ag2-copy && cp -R . /tmp/ag2-copy
python3 - <<'EOF'
p = "/tmp/ag2-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
n = '**A lease before any shared register.**'
assert n in t, "PLANT DID NOT LAND: ag2"
_planted = t.replace(n, '**Be careful with shared files.**', 1)
assert _planted != t, "PLANT DID NOT LAND: ag2"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ag2-copy/test/validate.py 2>&1 | grep -q 'lease rule is gone'; then
  echo "OK: validator FAILs — a worktree separates files and says nothing about who may edit the board"
else
  echo "ERROR: the shared registers lost the only rule that stops two agents overwriting each other"
  exit 1
fi
