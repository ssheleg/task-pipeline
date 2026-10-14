#!/usr/bin/env bash
# name: Negative self-test (a lesson refusal printing an absolute path)
set -eu
rm -rf /tmp/r13-say-refusal-copy && cp -R . /tmp/r13-say-refusal-copy
python3 - <<'EOF'
# Round 13, O: a refusal goes to stderr through the same redaction. Print it raw.
p = "/tmp/r13-say-refusal-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        print(f"lessons: {_say(str(exc))}", file=sys.stderr)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        print(f"lessons: {exc}", file=sys.stderr)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-say-refusal-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-say-refusal-copy
  echo "ERROR: lessons_test passed a refusal naming an absolute path"
  exit 1
else
  rm -rf /tmp/r13-say-refusal-copy
  echo "OK: lessons_test correctly FAILs — a refusal names the file"
fi
