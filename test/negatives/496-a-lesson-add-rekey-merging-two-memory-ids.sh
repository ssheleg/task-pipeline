#!/usr/bin/env bash
# name: Negative self-test (a lesson add re-key merging two memory ids)
set -eu
rm -rf /tmp/r13-rekey-two-add-copy && cp -R . /tmp/r13-rekey-two-add-copy
python3 - <<'EOF'
# Round 13, K: add never merges two different memory ids into one origin. Merge them.
p = "/tmp/r13-rekey-two-add-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                if n is None or (o.get("memory") and n.get("memory")\n                                 and mem_base(o["memory"]) != mem_base(n["memory"])):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                if n is None:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='K add: an old-key origin holding another id is not merged into the new one'
out=$(python3 /tmp/r13-rekey-two-add-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-rekey-two-add-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed add merging two store records into one origin"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — add keeps two memory ids two"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
