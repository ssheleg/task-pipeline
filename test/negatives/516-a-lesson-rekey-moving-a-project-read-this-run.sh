#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key moving a project read this run)
set -eu
rm -rf /tmp/r14-live-copy && cp -R . /tmp/r14-live-copy
python3 - <<'EOF'
# Round 14, F2: an origin whose project any checkout read this run holds is never re-keyed. Drop that.
p = "/tmp/r14-live-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = ' or o["project"] in live:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, ':\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-live-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-live-copy
  echo "ERROR: lessons_test passed a live project's origin moved into another"
  exit 1
else
  rm -rf /tmp/r14-live-copy
  echo "OK: lessons_test correctly FAILs — a project read this run is never moved"
fi
