#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild that one bad source refuses whole)
set -eu
rm -rf /tmp/rebuild-partial-copy && cp -R . /tmp/rebuild-partial-copy
python3 - <<'EOF'
# Round 6: one dangling commit or unreadable directory must not refuse the whole scan.
p = "/tmp/rebuild-partial-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if problems and not seen_files and not run["complete"]:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if problems or unresolved:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-partial-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-partial-copy
  echo "ERROR: lessons_test passed a rebuild that refuses everything over one bad source"
  exit 1
else
  rm -rf /tmp/rebuild-partial-copy
  echo "OK: lessons_test correctly FAILs — one bad source never costs the whole rebuild"
fi
