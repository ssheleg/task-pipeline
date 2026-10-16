#!/usr/bin/env bash
# name: Negative self-test (lesson add leaving one id on two live projects)
set -eu
rm -rf /tmp/r14-add-one-copy && cp -R . /tmp/r14-add-one-copy
python3 - <<'EOF'
# Round 14, F3: add keeps one memory id on one live project. Skip it.
p = "/tmp/r14-add-one-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        shared = _one_project_per_memory(entries, before)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        shared = []\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-add-one-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-add-one-copy
  echo "ERROR: lessons_test passed add leaving one id on two live projects"
  exit 1
else
  rm -rf /tmp/r14-add-one-copy
  echo "OK: lessons_test correctly FAILs — add keeps one id on one project"
fi
