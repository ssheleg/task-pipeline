#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key guessing between two repositories)
set -eu
rm -rf /tmp/r13-rekey-unique-copy && cp -R . /tmp/r13-rekey-unique-copy
python3 - <<'EOF'
# Round 13, K: the re-key needs exactly one candidate. Take the first of several.
p = "/tmp/r13-rekey-unique-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '    return hits[0] if len(hits) == 1 else None\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '    return hits[0] if hits else None\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-rekey-unique-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-rekey-unique-copy
  echo "ERROR: lessons_test passed a re-key guessing which repository an origin is"
  exit 1
else
  rm -rf /tmp/r13-rekey-unique-copy
  echo "OK: lessons_test correctly FAILs — an ambiguous origin is not re-keyed"
fi
