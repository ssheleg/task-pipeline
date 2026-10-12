#!/usr/bin/env bash
# name: Negative self-test (the publish disclosure section is deleted)
set -eu
rm -rf /tmp/ri10-copy && cp -R . /tmp/ri10-copy
python3 - <<'EOF'
p = "/tmp/ri10-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
n = '## `publish:` is a line in the verdict'
assert n in t, "PLANT DID NOT LAND: ri10"
_planted = t.replace(n, '## Publishing notes', 1)
assert _planted != t, "PLANT DID NOT LAND: ri10"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/ri10-copy/test/validate.py 2>&1 | grep -q 'no section giving publication'; then
  echo "OK: validator FAILs — an unarmed mechanism and one with nothing to say are indistinguishable"
else
  echo "ERROR: the rule went missing and nothing objected — an unarmed mechanism and one with nothing to say are indistinguishable"
  exit 1
fi
