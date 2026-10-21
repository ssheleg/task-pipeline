#!/usr/bin/env bash
# name: Negative self-test (a lesson newer-format notice printing an absolute path)
set -eu
rm -rf /tmp/r13-say-future-copy && cp -R . /tmp/r13-say-future-copy
python3 - <<'EOF'
# Round 13, O: the newer-format notice goes through the same redaction. Print it raw.
p = "/tmp/r13-say-future-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        print(_say(f"lessons: {len(future)}'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        print((f"lessons: {len(future)}', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='O: the newer index notice names the file, never its absolute path'
out=$(python3 /tmp/r13-say-future-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-say-future-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a newer-format notice naming an absolute path"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the newer-format notice names the file"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
