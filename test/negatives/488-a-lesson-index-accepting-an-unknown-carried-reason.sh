#!/usr/bin/env bash
# name: Negative self-test (a lesson index accepting an unknown carried reason)
set -eu
rm -rf /tmp/load-carried-copy && cp -R . /tmp/load-carried-copy
python3 - <<'EOF'
# Round 11/12: `carried` is one of CARRY_REASONS; any other value makes the line corrupt.
p = "/tmp/load-carried-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if "carried" in o and o["carried"] not in CARRY_REASONS:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/load-carried-copy/test/lessons_test.py; then
  rm -rf /tmp/load-carried-copy
  echo "ERROR: lessons_test passed an unknown carried reason"
  exit 1
else
  rm -rf /tmp/load-carried-copy
  echo "OK: lessons_test correctly FAILs — carried is checked against the enum"
fi
