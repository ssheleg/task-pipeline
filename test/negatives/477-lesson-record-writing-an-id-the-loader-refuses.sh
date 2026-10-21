#!/usr/bin/env bash
# name: Negative self-test (lesson record writing an id the loader refuses)
set -eu
rm -rf /tmp/record-memre-copy && cp -R . /tmp/record-memre-copy
python3 - <<'EOF'
# Round 12, H: record writes only an id MEM_RE accepts. Stop checking: the next read sets the whole index aside.
p = "/tmp/record-memre-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if not MEM_RE.fullmatch(memory):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='H: record refuses '\''mem:'\'' with exit 2; the other project'\''s id survives'
out=$(python3 /tmp/record-memre-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/record-memre-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed record writing an id the loader refuses"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — record validates the id like the loader"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
