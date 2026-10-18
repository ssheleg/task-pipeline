#!/usr/bin/env bash
# name: Negative self-test (a lesson add keeping a v1.95.0 origin as a second project)
set -eu
rm -rf /tmp/r13-rekey-add-copy && cp -R . /tmp/r13-rekey-add-copy
python3 - <<'EOF'
# Round 13, K: add re-keys a provenance-less origin of this repository. Skip it.
p = "/tmp/r13-rekey-add-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                n = None if o["project"] in known else _legacy_twin(o, fresh)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                n = None\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='K: add re-keys a v1.95.0 origin of this repository and keeps its id'
out=$(python3 /tmp/r13-rekey-add-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-rekey-add-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed add counting an upgraded origin as a second project"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — add re-keys an origin v1.95.0 wrote"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
