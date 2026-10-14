#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild printing absolute paths)
set -eu
rm -rf /tmp/abs-paths-copy && cp -R . /tmp/abs-paths-copy
python3 - <<'EOF'
# Round 12, E: rebuild names checkouts and files, never an absolute path. Stop redacting.
p = "/tmp/abs-paths-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    redact = lambda text: _redact(text, shown)  # noqa: E731\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    redact = lambda text: text  # noqa: E731\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/abs-paths-copy/test/lessons_test.py; then
  rm -rf /tmp/abs-paths-copy
  echo "ERROR: lessons_test passed a rebuild printing absolute paths"
  exit 1
else
  rm -rf /tmp/abs-paths-copy
  echo "OK: lessons_test correctly FAILs — messages carry names only"
fi
