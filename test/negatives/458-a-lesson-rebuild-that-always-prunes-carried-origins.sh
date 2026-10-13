#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild that always prunes carried origins)
set -eu
rm -rf /tmp/rebuild-prune-copy && cp -R . /tmp/rebuild-prune-copy
python3 - <<'EOF'
# Pruning carried origins is an explicit choice (--prune-carried). Make it the default.
p = "/tmp/rebuild-prune-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = "                elif a.prune_carried:\n"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "                elif True:\n", 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-prune-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-prune-copy
  echo "ERROR: lessons_test passed a rebuild that prunes carried origins without being asked"
  exit 1
else
  rm -rf /tmp/rebuild-prune-copy
  echo "OK: lessons_test correctly FAILs — carried origins leave only on --prune-carried"
fi
