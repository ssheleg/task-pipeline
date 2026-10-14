#!/usr/bin/env bash
# name: Negative self-test (lesson --prune-carried-reason offering a reason that never occurs)
set -eu
rm -rf /tmp/prune-source-copy && cp -R . /tmp/prune-source-copy
python3 - <<'EOF'
# Round 12: `source not read` is still accepted in a line but never produced; offering it as a prune reason promises a prune that can never happen.
p = "/tmp/prune-source-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = 'choices=PRUNE_REASONS, default=None,'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'choices=CARRY_REASONS, default=None,', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/prune-source-copy/test/lessons_test.py; then
  rm -rf /tmp/prune-source-copy
  echo "ERROR: lessons_test passed a prune reason that cannot occur"
  exit 1
else
  rm -rf /tmp/prune-source-copy
  echo "OK: lessons_test correctly FAILs — only produced reasons are offered"
fi
