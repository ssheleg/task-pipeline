#!/usr/bin/env bash
# name: Negative self-test (a lesson shallow check trusted when it times out)
set -eu
rm -rf /tmp/shallow-timeout-copy && cp -R . /tmp/shallow-timeout-copy
python3 - <<'EOF'
# Round 12: a shallow check that does not answer is refused — no source, a problem. Trust it instead (read the checkout as if not shallow).
p = "/tmp/shallow-timeout-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            unchecked.add(repo)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            continue\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='LOW: an unanswered shallow check derives nothing'
out=$(python3 /tmp/shallow-timeout-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/shallow-timeout-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a shallow check trusted on a timeout"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — an unanswered shallow check is refused"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
