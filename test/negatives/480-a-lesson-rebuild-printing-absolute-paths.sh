#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild printing absolute paths)
set -eu
rm -rf /tmp/abs-paths-copy && cp -R . /tmp/abs-paths-copy
python3 - <<'EOF'
# Round 12, E: rebuild names checkouts and files, never an absolute path. Stop redacting.
p = "/tmp/abs-paths-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        return _redact(text, shown)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        return text\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='E: rebuild names checkouts and files, never an absolute path'
out=$(python3 /tmp/abs-paths-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/abs-paths-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild printing absolute paths"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — messages carry names only"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
