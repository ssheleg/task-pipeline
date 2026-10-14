#!/usr/bin/env bash
# name: Negative self-test (a lesson memory id moved to another project's origin)
set -eu
rm -rf /tmp/rebuild-supersede-copy && cp -R . /tmp/rebuild-supersede-copy
python3 - <<'EOF'
# Round 11: no supersede, no move. Let a class's memory id follow it onto another project's origin (a stranger at the path, a re-initialised history), as the round-10 supersede did.
p = "/tmp/rebuild-supersede-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            ids = by_pc.get((project, ck), {})\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            ids = by_pc.get((project, ck), {}) or {b: r for (p, c), d in by_pc.items() if c == ck\n                                                   for b, r in d.items()}\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-supersede-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-supersede-copy
  echo "ERROR: lessons_test passed a memory id moved across projects"
  exit 1
else
  rm -rf /tmp/rebuild-supersede-copy
  echo "OK: lessons_test correctly FAILs — a memory id stays with its own project"
fi
