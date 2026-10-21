#!/usr/bin/env bash
# name: Negative self-test (a lesson partial rebuild moving a known project)
set -eu
rm -rf /tmp/r15-rb-copy && cp -R . /tmp/r15-rb-copy
python3 - <<'EOF'
# Round 15: a rebuild's live set includes every project the previous index records with provenance. Use this run's projects only.
p = "/tmp/r15-rb-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        rekeyed = _rekey_legacy(old, entries, set(run["project"].values()) | _known_projects(old))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        rekeyed = _rekey_legacy(old, entries, set(run["project"].values()))\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='F1c: an origin with provenance is never re-keyed'
out=$(python3 /tmp/r15-rb-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r15-rb-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a rebuild of X alone moving Y's id"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — a known project is never moved"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
