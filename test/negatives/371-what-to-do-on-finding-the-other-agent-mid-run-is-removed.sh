#!/usr/bin/env bash
# name: Negative self-test (what to do on finding the other agent mid-run is removed)
set -eu
rm -rf /tmp/ag3-copy && cp -R . /tmp/ag3-copy
python3 - <<'EOF'
p = "/tmp/ag3-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
n = 'leave their work alone'
assert n in t, "PLANT DID NOT LAND: ag3"
_planted = t.replace(n, 'proceed as you see fit', 1)
assert _planted != t, "PLANT DID NOT LAND: ag3"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ag3-copy/test/validate.py 2>&1 | grep -q 'mid-run is'; then
  echo "OK: validator FAILs — ending someone else's work to unblock your own is the asymmetry residue.md refuses"
else
  echo "ERROR: a run may now stage, revert or stash another agent's uncommitted work"
  exit 1
fi
