#!/usr/bin/env bash
# name: Negative self-test (a lesson query printing the absent index path)
set -eu
rm -rf /tmp/r14-query-copy && cp -R . /tmp/r14-query-copy
python3 - <<'EOF'
# Round 14, L3: query's absent-index line names the file. Print the path.
p = "/tmp/r14-query-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        print(_say(f"lessons: local index absent'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        print((f"lessons: local index absent', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='L3 query absent: the message names files, not absolute paths'
out=$(python3 /tmp/r14-query-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-query-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed query printing an absolute path"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — query names the file"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
