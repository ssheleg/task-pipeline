#!/usr/bin/env bash
# name: Negative self-test (an incomplete lesson rebuild dropping lessons the index held)
set -eu
rm -rf /tmp/rebuild-loss-copy && cp -R . /tmp/rebuild-loss-copy
python3 - <<'EOF'
# The narrow form of #116's conservation guard: a scan with unread sources must not silently
# replace a good projection with fewer lessons. Remove the guard; the suite must notice.
p = "/tmp/rebuild-loss-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = "        if incomplete and dropped and not a.force:\n"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "        if False:\n", 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-loss-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-loss-copy
  echo "ERROR: lessons_test passed an incomplete rebuild that drops lessons the index held"
  exit 1
else
  rm -rf /tmp/rebuild-loss-copy
  echo "OK: lessons_test correctly FAILs — an incomplete scan never silently drops a held lesson"
fi
