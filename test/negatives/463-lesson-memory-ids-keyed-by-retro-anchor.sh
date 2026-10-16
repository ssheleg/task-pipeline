#!/usr/bin/env bash
# name: Negative self-test (lesson memory ids keyed by retro anchor)
set -eu
rm -rf /tmp/rebuild-memanchor-copy && cp -R . /tmp/rebuild-memanchor-copy
python3 - <<'EOF'
# Round 8, M1: a memory id belongs to (project, classKey), the store's identity. Key it by the retro anchor again, across class keys.
p = "/tmp/rebuild-memanchor-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            ids = by_pc.get((project, ck), {})\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            ids = {m: r for (p, c), d in by_pc.items() if p == project for m, r in d.items()\n                   if r & {o["retro"] for o in e["origins"] if o["project"] == project}}\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-memanchor-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-memanchor-copy
  echo "ERROR: lessons_test passed memory ids keyed by retro anchor"
  exit 1
else
  rm -rf /tmp/rebuild-memanchor-copy
  echo "OK: lessons_test correctly FAILs — memory ids follow (project, classKey)"
fi
