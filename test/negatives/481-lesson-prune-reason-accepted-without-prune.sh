#!/usr/bin/env bash
# name: Negative self-test (lesson --prune-carried-reason accepted without --prune-carried)
set -eu
rm -rf /tmp/prune-alone-copy && cp -R . /tmp/prune-alone-copy
python3 - <<'EOF'
# Round 12: --prune-carried-reason narrows --prune-carried; alone it is a usage error.
p = "/tmp/prune-alone-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if a.cmd == "rebuild" and a.prune_carried_reason and not a.prune_carried:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/prune-alone-copy/test/lessons_test.py; then
  rm -rf /tmp/prune-alone-copy
  echo "ERROR: lessons_test passed a prune reason accepted alone"
  exit 1
else
  rm -rf /tmp/prune-alone-copy
  echo "OK: lessons_test correctly FAILs — the prune reason needs --prune-carried"
fi
