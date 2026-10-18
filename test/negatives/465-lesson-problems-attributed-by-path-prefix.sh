#!/usr/bin/env bash
# name: Negative self-test (lesson rebuild problems attributed by path prefix)
set -eu
rm -rf /tmp/rebuild-prefix-copy && cp -R . /tmp/rebuild-prefix-copy
python3 - <<'EOF'
# Round 9: a problem has a structural owner. Attribute it by name prefix again: an unreadable sibling `x-old` then makes checkout `x` not read, and x's own withdrawn entry gets the wrong reason.
p = "/tmp/rebuild-prefix-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    run["complete"] = {checkout_id(r) for r, whole in repos.items() if whole and r not in owners}\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    run["complete"] = {checkout_id(r) for r, whole in repos.items() if whole and r not in owners\n                       and not any(t.startswith(r.name) for _, t in problems)}\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='g2: x'\''s own withdrawn entry is carried as read-and-gone, not as unread'
out=$(python3 /tmp/rebuild-prefix-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-prefix-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed problems attributed by path prefix"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — problems carry a structural owner"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
