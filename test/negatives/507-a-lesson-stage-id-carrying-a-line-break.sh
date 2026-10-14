#!/usr/bin/env bash
# name: Negative self-test (a lesson stage id carrying a line break)
set -eu
rm -rf /tmp/r13-stage-text-copy && cp -R . /tmp/r13-stage-text-copy
python3 - <<'EOF'
# Round 13, P: a string stage id gets the text fields' checks. Drop them.
p = "/tmp/r13-stage-text-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                errs += _check_text(f"stages.{k}", st[k], '
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                errs += [] and _check_text(f"stages.{k}", st[k], ', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-stage-text-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-stage-text-copy
  echo "ERROR: lessons_test passed a stage id with a line break or a path"
  exit 1
else
  rm -rf /tmp/r13-stage-text-copy
  echo "OK: lessons_test correctly FAILs — a string stage id gets the text checks"
fi
