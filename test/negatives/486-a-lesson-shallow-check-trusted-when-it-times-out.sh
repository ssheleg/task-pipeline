#!/usr/bin/env bash
# name: Negative self-test (a lesson shallow check trusted when it times out)
set -eu
rm -rf /tmp/shallow-timeout-copy && cp -R . /tmp/shallow-timeout-copy
python3 - <<'EOF'
# Round 12: a shallow check that does not answer is refused — no source, a problem. Trust it instead (read the checkout as if not shallow).
p = "/tmp/shallow-timeout-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            unchecked.add(repo)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '            continue\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/shallow-timeout-copy/test/lessons_test.py; then
  rm -rf /tmp/shallow-timeout-copy
  echo "ERROR: lessons_test passed a shallow check trusted on a timeout"
  exit 1
else
  rm -rf /tmp/shallow-timeout-copy
  echo "OK: lessons_test correctly FAILs — an unanswered shallow check is refused"
fi
