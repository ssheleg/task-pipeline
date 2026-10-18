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
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='N1: an unreadable root'\''s origin is carried with its memory id, exit 0'
# Also accepted: both detect the revert; which fails first depends on the checkout the suite runs in.
also='J2: a re-init carries the old key with its id, counts one project, moves nothing'
out=$(python3 /tmp/rebuild-supersede-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/rebuild-supersede-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a memory id moved across projects"
  exit 1
elif printf '%s\n' "$out" | grep -qF -e "FAIL: $expect" -e "FAIL: $also"; then
  echo "OK: lessons_test correctly FAILs — a memory id stays with its own project"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
