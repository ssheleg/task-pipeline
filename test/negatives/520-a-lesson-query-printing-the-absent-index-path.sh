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
if python3 /tmp/r14-query-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-query-copy
  echo "ERROR: lessons_test passed query printing an absolute path"
  exit 1
else
  rm -rf /tmp/r14-query-copy
  echo "OK: lessons_test correctly FAILs — query names the file"
fi
