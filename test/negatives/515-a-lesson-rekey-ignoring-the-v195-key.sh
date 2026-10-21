#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key ignoring the key v1.95.0 would compute)
set -eu
rm -rf /tmp/r14-v195-copy && cp -R . /tmp/r14-v195-copy
python3 - <<'EOF'
# Round 14, F1: v1.95.0 must have computed the origin's key in that checkout. Drop that.
p = "/tmp/r14-v195-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        return (_legacy_key(c) == o["project"]\n                and '
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        return (True\n                and ', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='K: an old origin two projects could be is not re-keyed'
out=$(python3 /tmp/r14-v195-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-v195-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a re-key under a key v1.95.0 never gave"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the v1.95.0 key must match"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
