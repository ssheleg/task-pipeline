#!/usr/bin/env bash
# name: Negative self-test (INVERSION — the carve-out is a separate sentence, not a clause)
set -eu
rm -rf /tmp/res19-copy && cp -R . /tmp/res19-copy
python3 - <<'EOF'
p = "/tmp/res19-copy/plugins/task-pipeline/skills/task-pipeline/references/residue.md"
t = open(p, encoding="utf-8").read()
n = "**A foreign item never becomes spent.**"
assert n in t, "PLANT DID NOT LAND: res19"
# After the period, so a sentence-scoped guard cannot see it. The first
# version of that guard was sentence-scoped and this walked straight past.
_planted = t.replace(n, n + " Except when a container has been idle for more than a week.", 1)
assert _planted != t, "PLANT DID NOT LAND: res19"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res19-copy/test/validate.py 2>&1 | grep -q "exception marker"; then
  echo "OK: validator FAILs — the guard reads the whole span, not one sentence"
else
  echo "ERROR: a carve-out one period away from the rule was invisible"
  exit 1
fi
