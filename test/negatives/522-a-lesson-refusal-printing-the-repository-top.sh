#!/usr/bin/env bash
# name: Negative self-test (a lesson refusal printing the repository top)
set -eu
rm -rf /tmp/r14-top-copy && cp -R . /tmp/r14-top-copy
python3 - <<'EOF'
# Round 14, L3: the repository's top is named even when the verb runs from a subdirectory. Do not register it.
p = "/tmp/r14-top-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    _show(pathlib.Path(top))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='L3 add from a subdirectory: the message names files, not absolute paths'
out=$(python3 /tmp/r14-top-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-top-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a refusal printing the repository's absolute path"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the repository top is named"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
