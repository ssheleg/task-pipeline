#!/usr/bin/env bash
# name: Negative self-test (a lesson duplicate tie depending on line order)
set -eu
rm -rf /tmp/r13-tie-break-copy && cp -R . /tmp/r13-tie-break-copy
python3 - <<'EOF'
# Round 13, Q: a same-revision tie keeps the lexically smaller id. Let the line order decide.
p = "/tmp/r13-tie-break-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                -mem_rev(x.get("memory") or ""), x.get("memory") or "", json.dumps(x, sort_keys=True)))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                -mem_rev(x.get("memory") or ""),))\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='Q: the dropped id is named'
out=$(python3 /tmp/r13-tie-break-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-tie-break-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a kept id that depends on the order of lines"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — a same-revision tie is deterministic"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
