#!/usr/bin/env bash
# name: Negative self-test (lesson --prune-carried-reason taking any string)
set -eu
rm -rf /tmp/prune-choices-copy && cp -R . /tmp/prune-choices-copy
python3 - <<'EOF'
# Round 12: --prune-carried-reason accepts only the reasons a rebuild produces. Accept any.
p = "/tmp/prune-choices-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = 'choices=PRUNE_REASONS, default=None,'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'default=None,', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/prune-choices-copy/test/lessons_test.py; then
  rm -rf /tmp/prune-choices-copy
  echo "ERROR: lessons_test passed a prune reason that is any string"
  exit 1
else
  rm -rf /tmp/prune-choices-copy
  echo "OK: lessons_test correctly FAILs — the prune reason is one of the produced reasons"
fi
