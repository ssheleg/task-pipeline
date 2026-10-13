#!/usr/bin/env bash
# name: Negative self-test (lesson status that ignores carried origins)
set -eu
rm -rf /tmp/rebuild-status-copy && cp -R . /tmp/rebuild-status-copy
python3 - <<'EOF'
# A lesson two projects hold stays a candidate while one project's root is unreadable: status,
# projects and seen count carried origins. Count only re-derived ones; the suite must notice.
p = "/tmp/rebuild-status-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    projects = len({o["project"] for o in origins})\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(
    needle, '    projects = max(1, len({o["project"] for o in origins if not o.get("carried")}))\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-status-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-status-copy
  echo "ERROR: lessons_test passed a status computed without carried origins"
  exit 1
else
  rm -rf /tmp/rebuild-status-copy
  echo "OK: lessons_test correctly FAILs — status counts carried origins"
fi
