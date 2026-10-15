#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key ignoring the key v1.95.0 would compute)
set -eu
rm -rf /tmp/r14-v195-copy && cp -R . /tmp/r14-v195-copy
python3 - <<'EOF'
# Round 14, F1: v1.95.0 must have computed the origin's key in that checkout. Drop that.
p = "/tmp/r14-v195-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = ' and _legacy_key(c) == o["project"]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-v195-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-v195-copy
  echo "ERROR: lessons_test passed a re-key under a key v1.95.0 never gave"
  exit 1
else
  rm -rf /tmp/r14-v195-copy
  echo "OK: lessons_test correctly FAILs — the v1.95.0 key must match"
fi
