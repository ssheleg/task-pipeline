#!/usr/bin/env bash
# name: Negative self-test (a lesson origin called a stranger though its commit resolves there)
set -eu
rm -rf /tmp/foreign-resolves-copy && cp -R . /tmp/foreign-resolves-copy
python3 - <<'EOF'
# Round 12: `checkout holds another project` only when the origin's own commit does not resolve in that checkout. Drop that condition.
p = "/tmp/foreign-resolves-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        elif run["project"][c] != o["project"] and not _resolves_in(c, o["commit"]):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        elif run["project"][c] != o["project"]:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='F pages-no-main: a checkout on another branch is not a stranger'
out=$(python3 /tmp/foreign-resolves-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/foreign-resolves-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a stranger called on a key alone"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the same repository under another key is not a stranger"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
