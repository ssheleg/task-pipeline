#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild removing an origin by a project-level read set)
set -eu
rm -rf /tmp/rebuild-readset-copy && cp -R . /tmp/rebuild-readset-copy
python3 - <<'EOF'
# Round 9: implicit removal needs positive evidence from the SAME checkout. Let any checkout that read the same retro path decide instead.
p = "/tmp/rebuild-readset-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if c not in run["complete"] or rel not in run["files"].get(c, ()):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if not run["complete"] or rel not in set().union(*run["files"].values()):\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-readset-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-readset-copy
  echo "ERROR: lessons_test passed a rebuild that removes by a project-level read set"
  exit 1
else
  rm -rf /tmp/rebuild-readset-copy
  echo "OK: lessons_test correctly FAILs — only the origin's own checkouts decide"
fi
