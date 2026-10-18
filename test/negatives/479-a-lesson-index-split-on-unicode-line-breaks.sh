#!/usr/bin/env bash
# name: Negative self-test (a lesson index split on Unicode line breaks)
set -eu
rm -rf /tmp/load-split-copy && cp -R . /tmp/load-split-copy
python3 - <<'EOF'
# Round 12, B: the index is split on \n only, as dump writes it. Use str.splitlines() again: a U+2028 inside a value makes every read call the index corrupt.
p = "/tmp/load-split-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    for i, line in enumerate(text.split("\\n"), 1):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    for i, line in enumerate(text.splitlines(), 1):\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='B: a separator inside a value is not a line'
out=$(python3 /tmp/load-split-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/load-split-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an index split on U+2028"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the index is split on \n only"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
