#!/usr/bin/env bash
# name: Negative self-test (one lesson memory id left on two class keys)
set -eu
rm -rf /tmp/rebuild-memtwice-copy && cp -R . /tmp/rebuild-memtwice-copy
python3 - <<'EOF'
# One memory id is one store record, so it belongs to one class key. Stop repairing an index that holds it on two.
p = "/tmp/rebuild-memtwice-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if m and holders[mem_base(m)][0] != ck:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='one memory id is never attached to two class keys'
out=$(python3 /tmp/rebuild-memtwice-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-memtwice-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed one memory id on two class keys"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — one memory id stays on one class key"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
