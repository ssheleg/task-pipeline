#!/usr/bin/env bash
# name: Negative self-test (a lesson session note printing an absolute path)
set -eu
rm -rf /tmp/r13-say-notes-copy && cp -R . /tmp/r13-say-notes-copy
python3 - <<'EOF'
# Round 13, O: the session's notes go to stderr through the same redaction. Print them raw.
p = "/tmp/r13-say-notes-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            print(f"lessons: {_say(n)}", file=sys.stderr)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            print(f"lessons: {n}", file=sys.stderr)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='the index is moved once, and the move is said'
out=$(python3 /tmp/r13-say-notes-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-say-notes-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a corrupt-index notice naming an absolute path"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — session notes name files, not paths"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
