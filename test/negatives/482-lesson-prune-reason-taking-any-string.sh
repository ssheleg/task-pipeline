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
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='LOW: --prune-carried-reason an unknown reason is a usage error'
out=$(python3 /tmp/prune-choices-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/prune-choices-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a prune reason that is any string"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the prune reason is one of the produced reasons"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
