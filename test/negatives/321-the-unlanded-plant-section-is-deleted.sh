#!/usr/bin/env bash
# name: Negative self-test (the unlanded-plant section is deleted)
set -eu
rm -rf /tmp/ri03-copy && cp -R . /tmp/ri03-copy
python3 - <<'EOF'
p = "/tmp/ri03-copy/plugins/task-pipeline/skills/task-pipeline/references/probing.md"
t = open(p, encoding="utf-8").read()
n = '## A green probe is evidence only if'
assert n in t, "PLANT DID NOT LAND: ri03"
_planted = t.replace(n, '## Probes and greens', 1)
assert _planted != t, "PLANT DID NOT LAND: ri03"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri03-copy/test/validate.py 2>&1 | grep -q 'no section on a green probe'; then
  echo "OK: validator FAILs — a plant that missed reports the same green as a sound check"
else
  echo "ERROR: the rule went missing and nothing objected — a plant that missed reports the same green as a sound check"
  exit 1
fi
