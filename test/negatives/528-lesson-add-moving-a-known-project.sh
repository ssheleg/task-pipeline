#!/usr/bin/env bash
# name: Negative self-test (lesson add moving a known project)
set -eu
rm -rf /tmp/r15-add-copy && cp -R . /tmp/r15-add-copy
python3 - <<'EOF'
# Round 15: add never re-keys an origin whose key is a project the index records with provenance. Drop the check.
p = "/tmp/r15-add-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                n = None if o["project"] in known else _legacy_twin(o, fresh)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                n = _legacy_twin(o, fresh)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='F2 add in X: a known project'\''s origin is never re-keyed'
out=$(python3 /tmp/r15-add-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r15-add-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an add in X moving Y's id"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — add never moves a known project"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
