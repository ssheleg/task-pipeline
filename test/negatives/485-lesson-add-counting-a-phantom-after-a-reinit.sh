#!/usr/bin/env bash
# name: Negative self-test (lesson add counting a phantom project after a re-init)
set -eu
rm -rf /tmp/add-foreign-copy && cp -R . /tmp/add-foreign-copy
python3 - <<'EOF'
# Round 12, G: add marks this checkout's old-key origin, whose commit no longer resolves, as `checkout holds another project`. Stop: add counts a phantom until the next rebuild.
p = "/tmp/add-foreign-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                      if o["project"] != project and here in (o.get("checkouts") or [])\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                      if False and here in (o.get("checkouts") or [])\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='LOW: add after a re-init counts one project'
out=$(python3 /tmp/add-foreign-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/add-foreign-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed add counting a phantom project"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — add applies the stranger rule"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
