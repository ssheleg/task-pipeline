#!/usr/bin/env bash
# name: Negative self-test (lesson memory ids compared with their revision)
set -eu
rm -rf /tmp/rebuild-memrev-copy && cp -R . /tmp/rebuild-memrev-copy
python3 - <<'EOF'
# Round 9: ids compare on the part before `@`, the highest revision winning. Compare the whole string again.
p = "/tmp/rebuild-memrev-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    return memory.rsplit("@", 1)[0]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    return memory\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='B6 fixture: revision 2 recorded'
out=$(python3 /tmp/rebuild-memrev-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-memrev-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed memory ids compared with their @revision"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — one id carries one revision"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
