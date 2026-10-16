#!/usr/bin/env bash
# name: Negative self-test (lesson duplicate lines dropping a memory id silently)
set -eu
rm -rf /tmp/dup-dropped-copy && cp -R . /tmp/dup-dropped-copy
python3 - <<'EOF'
# Round 12: merging two lines for one origin names every memory id it drops. Stop naming it.
p = "/tmp/dup-dropped-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            if other.get("memory") and mem_base(other["memory"]) != mem_base(keep.get("memory") or ""):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            if False:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/dup-dropped-copy/test/lessons_test.py; then
  rm -rf /tmp/dup-dropped-copy
  echo "ERROR: lessons_test passed a merge that drops an id without saying so"
  exit 1
else
  rm -rf /tmp/dup-dropped-copy
  echo "OK: lessons_test correctly FAILs — a dropped id is named"
fi
