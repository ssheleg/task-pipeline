#!/usr/bin/env bash
# name: Negative self-test (a lesson add keeping a v1.95.0 origin as a second project)
set -eu
rm -rf /tmp/r13-rekey-add-copy && cp -R . /tmp/r13-rekey-add-copy
python3 - <<'EOF'
# Round 13, K: add re-keys a provenance-less origin of this repository. Skip it.
p = "/tmp/r13-rekey-add-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                n = _legacy_twin(o, fresh)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                n = None\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-rekey-add-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-rekey-add-copy
  echo "ERROR: lessons_test passed add counting an upgraded origin as a second project"
  exit 1
else
  rm -rf /tmp/r13-rekey-add-copy
  echo "OK: lessons_test correctly FAILs — add re-keys an origin v1.95.0 wrote"
fi
