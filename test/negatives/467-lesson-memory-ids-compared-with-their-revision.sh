#!/usr/bin/env bash
# name: Negative self-test (lesson memory ids compared with their revision)
set -eu
rm -rf /tmp/rebuild-memrev-copy && cp -R . /tmp/rebuild-memrev-copy
python3 - <<'EOF'
# Round 9: ids compare on the part before `@`, the highest revision winning. Compare the whole string again.
p = "/tmp/rebuild-memrev-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    return memory.rsplit("@", 1)[0]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    return memory\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/rebuild-memrev-copy/test/lessons_test.py; then
  rm -rf /tmp/rebuild-memrev-copy
  echo "ERROR: lessons_test passed memory ids compared with their @revision"
  exit 1
else
  rm -rf /tmp/rebuild-memrev-copy
  echo "OK: lessons_test correctly FAILs — one id carries one revision"
fi
