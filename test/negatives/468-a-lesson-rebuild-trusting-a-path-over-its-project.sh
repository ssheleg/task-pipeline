#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild trusting a checkout path over the project checked out there)
set -eu
rm -rf /tmp/rebuild-foreign-copy && cp -R . /tmp/rebuild-foreign-copy
python3 - <<'EOF'
# Round 10: a path is not an identity. Stop noticing that a checkout now holds another project.
p = "/tmp/rebuild-foreign-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        elif run["project"][c] != o["project"] and not _resolves_in(c, o["commit"]):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        elif False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='F1: a different project at the same path decides nothing; A'\''s origin carried, not counted'
out=$(python3 /tmp/rebuild-foreign-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-foreign-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild blind to a stranger at the same path"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — a stranger at the path is named as one"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
