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
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='LOW: --prune-carried-reason a reason that cannot occur is a usage error'
out=$(python3 /tmp/prune-source-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/prune-source-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a prune reason that cannot occur"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — only produced reasons are offered"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
