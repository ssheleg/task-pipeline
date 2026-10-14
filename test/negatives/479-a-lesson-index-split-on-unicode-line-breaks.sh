#!/usr/bin/env bash
# name: Negative self-test (a lesson index split on Unicode line breaks)
set -eu
rm -rf /tmp/load-split-copy && cp -R . /tmp/load-split-copy
python3 - <<'EOF'
# Round 12, B: the index is split on \n only, as dump writes it. Use str.splitlines() again: a U+2028 inside a value makes every read call the index corrupt.
p = "/tmp/load-split-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    for i, line in enumerate(text.split("\\n"), 1):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    for i, line in enumerate(text.splitlines(), 1):\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/load-split-copy/test/lessons_test.py; then
  rm -rf /tmp/load-split-copy
  echo "ERROR: lessons_test passed an index split on U+2028"
  exit 1
else
  rm -rf /tmp/load-split-copy
  echo "OK: lessons_test correctly FAILs — the index is split on \n only"
fi
