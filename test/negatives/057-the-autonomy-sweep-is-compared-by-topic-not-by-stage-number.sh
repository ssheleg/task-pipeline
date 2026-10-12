#!/usr/bin/env bash
# name: Negative self-test (the autonomy sweep is compared by topic, not by stage number)
set -eu
rm -rf /tmp/sweep-copy-2 && cp -R . /tmp/sweep-copy-2
python3 - <<'EOF'
p = "/tmp/sweep-copy-2/plugins/task-pipeline/skills/task-pipeline/references/grill.md"
t = open(p, encoding="utf-8").read()
old = "| 0 Docs regime |"
assert old in t, "PLANT MISSED"
i = t.index(old); j = t.index("\n", i) + 1
open(p, "w", encoding="utf-8").write(t[:i] + t[j:])
EOF
if python3 /tmp/sweep-copy-2/test/validate.py; then
  echo "ERROR: validator passed a sweep row the brief records and the grill never asks — both files still 'cover stage 0', which is why counting stage numbers was not enough"
  exit 1
else
  echo "OK: validator compares the sweep per stage as a topic set"
fi
