#!/usr/bin/env bash
# name: Negative self-test (a lesson foreign holder counted as live)
set -eu
rm -rf /tmp/r15-m10-copy && cp -R . /tmp/r15-m10-copy
python3 - <<'EOF'
# Round 15, m10: an origin carried as `checkout holds another project` is not a live holder of its id. Count it.
p = "/tmp/r15-m10-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if o.get("memory") and o.get("carried") != CARRY_FOREIGN:\n                live.setdefault'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if o.get("memory"):\n                live.setdefault', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='m10: after the re-attach a rebuild keeps the id on the new origin'
out=$(python3 /tmp/r15-m10-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r15-m10-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a re-attached id stripped from its new origin"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — a foreign holder is not live"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
