#!/usr/bin/env bash
# name: Negative self-test (a stage dropping a reader state)
set -eu
rm -rf /tmp/rd2-copy && cp -R . /tmp/rd2-copy
python3 - <<'EOF'
p = "/tmp/rd2-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert "`reader: none found`" in t, "PLANT DID NOT LAND: the stage's reader states moved"
open(p, "w", encoding="utf-8").write(t.replace("`reader: none found`", "a clean verdict", 1))
EOF
if python3 /tmp/rd2-copy/test/validate.py; then
  echo "ERROR: a state the doctrine defines and no stage emits is a state nobody records"
  exit 1
else
  echo "OK: validator correctly FAILs — every reader state is named by the stage"
fi
