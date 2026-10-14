#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild trusting a checkout path over the project checked out there)
set -eu
rm -rf /tmp/rebuild-foreign-copy && cp -R . /tmp/rebuild-foreign-copy
python3 - <<'EOF'
# Round 10: a path is not an identity. Stop noticing that a checkout now holds another project.
p = "/tmp/rebuild-foreign-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        elif run["project"][c] != o["project"]:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        elif False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-foreign-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-foreign-copy
  echo "ERROR: lessons_test passed a rebuild blind to a stranger at the same path"
  exit 1
else
  rm -rf /tmp/rebuild-foreign-copy
  echo "OK: lessons_test correctly FAILs — a stranger at the path is named as one"
fi
