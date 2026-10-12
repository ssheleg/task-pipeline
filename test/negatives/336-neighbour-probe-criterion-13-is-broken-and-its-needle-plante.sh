#!/usr/bin/env bash
# name: Negative self-test (NEIGHBOUR PROBE — criterion 13 is broken and its needle planted just outside the item)
set -eu
rm -rf /tmp/res4-copy && cp -R . /tmp/res4-copy
python3 - <<'EOF'
p = "/tmp/res4-copy/plugins/task-pipeline/skills/task-pipeline/references/acceptance.md"
t = open(p, encoding="utf-8").read()
n = '**reported, never ended**'
assert n in t, "PLANT DID NOT LAND: res4"
_planted = t.replace(n, 'cleaned up as well', 1)
_planted = _planted.replace('## When the answer is "something\'s missing"',
    "<!-- eight classes enumerated \u00b7 reported, never ended -->\n\n"
    '## When the answer is "something\'s missing"', 1)
assert _planted != t, "PLANT DID NOT LAND: res4"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res4-copy/test/validate.py 2>&1 | grep -q 'lost one of its halves'; then
  echo "OK: validator FAILs — the guard reads the item, not the region before the next heading"
else
  echo "ERROR: the guard was answered by text parked outside criterion 13 — positional narrowing is not scoping"
  exit 1
fi
