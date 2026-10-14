#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild trusting a checkout path over the project checked out there)
set -eu
rm -rf /tmp/rebuild-foreign-copy && cp -R . /tmp/rebuild-foreign-copy
python3 - <<'EOF'
# Round 10, F1: a path is not an identity. Let a different project at the same path show another project's origin gone.
p = "/tmp/rebuild-foreign-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if (c not in run["complete"] or run["project"][c] != o["project"]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if (c not in run["complete"]\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-foreign-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-foreign-copy
  echo "ERROR: lessons_test passed a rebuild that lets a foreign project decide"
  exit 1
else
  rm -rf /tmp/rebuild-foreign-copy
  echo "OK: lessons_test correctly FAILs — only the origin's own project at that path decides"
fi
