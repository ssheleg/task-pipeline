#!/usr/bin/env bash
# name: Negative self-test (lesson record re-attaching an id from another checkout)
set -eu
rm -rf /tmp/r13-record-here-copy && cp -R . /tmp/r13-record-here-copy
python3 - <<'EOF'
# Round 13, M: record's re-attach exception holds only at the carried origin's own checkout. Allow it from anywhere.
p = "/tmp/r13-record-here-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                          and not (y.get("carried") == CARRY_FOREIGN and here in (y.get("checkouts") or []))})\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                          and y.get("carried") != CARRY_FOREIGN})\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-record-here-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-record-here-copy
  echo "ERROR: lessons_test passed a project elsewhere taking a carried origin's id"
  exit 1
else
  rm -rf /tmp/r13-record-here-copy
  echo "OK: lessons_test correctly FAILs — the re-attach holds only at the same checkout"
fi
