#!/usr/bin/env bash
# name: Negative self-test (lesson emit and record ignoring the origin that holds the memory id)
set -eu
rm -rf /tmp/rebuild-thisorigin-copy && cp -R . /tmp/rebuild-thisorigin-copy
python3 - <<'EOF'
# Round 9: emit and record use the origin of the project that holds the memory id. Pick the first by (project, retro) again.
p = "/tmp/rebuild-thisorigin-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    return sorted(mine, key=lambda o: (not o.get("memory"), _origin_key(o)))[0]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    return sorted(mine, key=_origin_key)[0]\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='B4: emit after add revises mem:b4'
out=$(python3 /tmp/rebuild-thisorigin-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-thisorigin-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed emit that ignores the recorded origin"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — emit revises the record the store already has"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
