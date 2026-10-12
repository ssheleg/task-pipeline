#!/usr/bin/env bash
# name: Negative self-test (the behaviour-or-reporting field loses one of its two values)
set -eu
rm -rf /tmp/r6a-copy && cp -R . /tmp/r6a-copy
python3 - <<'EOF'
p = "/tmp/r6a-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = 'One of two words per finding, `behaviour` or `reporting`,'
assert n in t, "PLANT DID NOT LAND: r6a"
_planted = t.replace(n, 'One word per finding, `behaviour`,', 1)
assert _planted != t, "PLANT DID NOT LAND: r6a"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/r6a-copy/test/validate.py 2>&1 | grep -q 'both values as a pair'; then
  echo "OK: validator FAILs — one value cannot distinguish a fix from a note"
else
  echo "ERROR: R-006 got a field that cannot answer the question it exists for"
  exit 1
fi
