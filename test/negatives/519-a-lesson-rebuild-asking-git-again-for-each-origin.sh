#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild asking git again for each origin)
set -eu
rm -rf /tmp/r14-cache-copy && cp -R . /tmp/r14-cache-copy
python3 - <<'EOF'
# Round 14, L2: one git question per (checkout, commit) in a run. Ask every time.
p = "/tmp/r14-cache-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    if key not in _RESOLVES:\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    if True:\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-cache-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-cache-copy
  echo "ERROR: lessons_test passed a rebuild asking git the same question again"
  exit 1
else
  rm -rf /tmp/r14-cache-copy
  echo "OK: lessons_test correctly FAILs — git is asked once per (checkout, commit)"
fi
