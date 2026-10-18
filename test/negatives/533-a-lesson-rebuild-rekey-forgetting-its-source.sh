#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild re-key forgetting its source)
set -eu
rm -rf /tmp/r16-src-rb-copy && cp -R . /tmp/r16-src-rb-copy
python3 - <<'EOF'
# Round 16: the reclaim. Put back a lesson rebuild re-key forgetting its source.
p = "/tmp/r16-src-rb-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                moved["rekeyedFrom"] = o.get("rekeyedFrom") or o["project"]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                pass\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r16 rebuild of X alone: X read first re-keys the id and records its source'
out=$(python3 /tmp/r16-src-rb-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r16-src-rb-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a re-key that cannot be undone"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, a rebuild re-key records its source"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
