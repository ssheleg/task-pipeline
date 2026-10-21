#!/usr/bin/env bash
# name: Negative self-test (lesson record re-attaching an id from another checkout)
set -eu
rm -rf /tmp/r13-record-here-copy && cp -R . /tmp/r13-record-here-copy
python3 - <<'EOF'
# Round 13, M: record's re-attach exception holds only at the carried origin's own checkout. Allow it from anywhere.
p = "/tmp/r13-record-here-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                          and not (y.get("carried") == CARRY_FOREIGN and here in (y.get("checkouts") or []))})\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                          and y.get("carried") != CARRY_FOREIGN})\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='M: a project at another checkout never takes an id a carried origin holds'
out=$(python3 /tmp/r13-record-here-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-record-here-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a project elsewhere taking a carried origin's id"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — the re-attach holds only at the same checkout"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
