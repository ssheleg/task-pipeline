#!/usr/bin/env bash
# name: Negative self-test (a lesson project counted complete because one of its checkouts read)
set -eu
rm -rf /tmp/rebuild-anycheckout-copy && cp -R . /tmp/rebuild-anycheckout-copy
python3 - <<'EOF'
# Round 8, H1: every clone and worktree shares the project key, so a project is complete only when EVERY checkout of it read. Count it complete when any one did.
p = "/tmp/rebuild-anycheckout-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if all(repos[r] and r not in failed for r, p in project_of.items() if p == project):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if any(repos[r] and r not in failed for r, p in project_of.items() if p == project):\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-anycheckout-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-anycheckout-copy
  echo "ERROR: lessons_test passed a project complete because one checkout read"
  exit 1
else
  rm -rf /tmp/rebuild-anycheckout-copy
  echo "OK: lessons_test correctly FAILs — one checkout never decides for another"
fi
