#!/usr/bin/env bash
# name: Negative self-test (a lesson memory id kept by the later holder)
set -eu
rm -rf /tmp/r13-earlier-holder-copy && cp -R . /tmp/r13-earlier-holder-copy
python3 - <<'EOF'
# Round 13, M/M2: the earlier holder keeps the id. Keep it on the later one.
p = "/tmp/r13-earlier-holder-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            keep = (sorted(projects & first.get(base, set())) or sorted(projects))[0]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            keep = (sorted(projects - first.get(base, set())) or sorted(projects))[0]\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-earlier-holder-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-earlier-holder-copy
  echo "ERROR: lessons_test passed the later holder taking the id"
  exit 1
else
  rm -rf /tmp/r13-earlier-holder-copy
  echo "OK: lessons_test correctly FAILs — the project that held the id first keeps it"
fi
