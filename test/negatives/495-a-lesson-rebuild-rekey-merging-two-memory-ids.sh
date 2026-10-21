#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild re-key merging two memory ids)
set -eu
rm -rf /tmp/r13-rekey-two-rb-copy && cp -R . /tmp/r13-rekey-two-rb-copy
python3 - <<'EOF'
# Round 13, K: a re-key never merges two different memory ids. Merge them.
p = "/tmp/r13-rekey-two-rb-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if (twin and twin.get("memory") and o.get("memory")\n                    and mem_base(twin["memory"]) != mem_base(o["memory"])):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='K rebuild: an old-key origin holding another id is not merged into the new one'
out=$(python3 /tmp/r13-rekey-two-rb-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-rekey-two-rb-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild merging two store records into one origin"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — two memory ids stay two"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
