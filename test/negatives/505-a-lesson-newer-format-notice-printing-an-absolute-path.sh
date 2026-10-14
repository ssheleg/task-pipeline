#!/usr/bin/env bash
# name: Negative self-test (a lesson newer-format notice printing an absolute path)
set -eu
rm -rf /tmp/r13-say-future-copy && cp -R . /tmp/r13-say-future-copy
python3 - <<'EOF'
# Round 13, O: the newer-format notice goes through the same redaction. Print it raw.
p = "/tmp/r13-say-future-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        print(_say(f"lessons: {len(future)}'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        print((f"lessons: {len(future)}', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-say-future-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-say-future-copy
  echo "ERROR: lessons_test passed a newer-format notice naming an absolute path"
  exit 1
else
  rm -rf /tmp/r13-say-future-copy
  echo "OK: lessons_test correctly FAILs — the newer-format notice names the file"
fi
