#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild leaving one id on two live projects)
set -eu
rm -rf /tmp/r13-one-project-copy && cp -R . /tmp/r13-one-project-copy
python3 - <<'EOF'
# Round 13, M/M2: a rebuild keeps one memory id on one live project. Skip that invariant.
p = "/tmp/r13-one-project-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        shared = _one_project_per_memory(entries, old)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        shared = []\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-one-project-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-one-project-copy
  echo "ERROR: lessons_test passed one memory id on two live projects"
  exit 1
else
  rm -rf /tmp/r13-one-project-copy
  echo "OK: lessons_test correctly FAILs — one id is one project's record"
fi
