#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key guessing between two repositories)
set -eu
rm -rf /tmp/r13-rekey-unique-copy && cp -R . /tmp/r13-rekey-unique-copy
python3 - <<'EOF'
# Round 13, K: the re-key needs exactly one candidate. Take the first of several.
p = "/tmp/r13-rekey-unique-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    return hits[0] if len(hits) == 1 else None\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    return hits[0] if hits else None\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='F1d: an origin two repositories could each be is never re-keyed'
out=$(python3 /tmp/r13-rekey-unique-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-rekey-unique-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a re-key guessing which repository an origin is"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — an ambiguous origin is not re-keyed"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
