#!/usr/bin/env bash
# name: Negative self-test (a lesson index setting aside a v1.95.0 stage id)
set -eu
rm -rf /tmp/r14-migrate-copy && cp -R . /tmp/r14-migrate-copy
python3 - <<'EOF'
# Round 14, L5: a stage id v1.95.0 accepted is normalised on read. Read it as it is.
p = "/tmp/r14-migrate-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        _migrate_stages(e, notes)\n        if not _entry_shape(e):'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if not _entry_shape(e):', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-migrate-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-migrate-copy
  echo "ERROR: lessons_test passed an upgraded index set aside as corrupt"
  exit 1
else
  rm -rf /tmp/r14-migrate-copy
  echo "OK: lessons_test correctly FAILs — an old stage id is normalised on read"
fi
