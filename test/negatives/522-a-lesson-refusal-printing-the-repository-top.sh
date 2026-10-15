#!/usr/bin/env bash
# name: Negative self-test (a lesson refusal printing the repository top)
set -eu
rm -rf /tmp/r14-top-copy && cp -R . /tmp/r14-top-copy
python3 - <<'EOF'
# Round 14, L3: the repository's top is named even when the verb runs from a subdirectory. Do not register it.
p = "/tmp/r14-top-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    _show(pathlib.Path(top))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r14-top-copy/test/lessons_test.py; then
  rm -rf /tmp/r14-top-copy
  echo "ERROR: lessons_test passed a refusal printing the repository's absolute path"
  exit 1
else
  rm -rf /tmp/r14-top-copy
  echo "OK: lessons_test correctly FAILs — the repository top is named"
fi
