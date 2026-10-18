#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key moving a project read this run)
set -eu
rm -rf /tmp/r14-live-copy && cp -R . /tmp/r14-live-copy
python3 - <<'EOF'
# Round 14, F2: an origin whose project any checkout read this run holds is never re-keyed. Drop that.
p = "/tmp/r14-live-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if o["project"] in live:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='F1c: an origin with provenance is never re-keyed'
out=$(python3 /tmp/r14-live-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r14-live-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a live project's origin moved into another"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — a project read this run is never moved"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
