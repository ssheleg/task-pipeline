#!/usr/bin/env bash
# name: Negative self-test (a lesson title carrying a Unicode line separator)
set -eu
rm -rf /tmp/text-sep-copy && cp -R . /tmp/text-sep-copy
python3 - <<'EOF'
# Round 12, B: lesson/1 text refuses every separator str.splitlines() breaks on. Check only \n and \r again.
p = "/tmp/text-sep-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if value != "".join(value.splitlines()) or any(ch in value for ch in "\\r\\n"):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if any(ch in value for ch in "\\r\\n"):\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='B: a title carrying '\''\u2028'\'' is refused, nothing written'
out=$(python3 /tmp/text-sep-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/text-sep-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a title carrying U+2028"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — U+2028/U+2029/U+0085 are line breaks"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
