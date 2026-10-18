#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild that drops origins it could not re-derive)
set -eu
rm -rf /tmp/rebuild-loss-copy && cp -R . /tmp/rebuild-loss-copy
python3 - <<'EOF'
# Rounds 7/11: rebuild never removes anything on its own. Drop the carried origins instead.
p = "/tmp/rebuild-loss-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                    carried.append((ck, rec))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                    pass\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='a readable empty scope carries the held lesson'
out=$(python3 /tmp/rebuild-loss-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-loss-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild that drops origins it could not re-derive"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — every origin not re-derived is carried"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
