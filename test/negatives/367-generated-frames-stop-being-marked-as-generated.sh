#!/usr/bin/env bash
# name: Negative self-test (generated frames stop being marked as generated)
set -eu
rm -rf /tmp/fig4-copy && cp -R . /tmp/fig4-copy
python3 - <<'EOF'
p = "/tmp/fig4-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
n = 'marked as coming from implementation'
assert n in t, "PLANT DID NOT LAND: fig4"
_planted = t.replace(n, 'added', 1)
assert _planted != t, "PLANT DID NOT LAND: fig4"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fig4-copy/test/validate.py 2>&1 | grep -q 'lost a half'; then
  echo "OK: validator FAILs — a designer must tell a decision from a generation"
else
  echo "ERROR: an unmarked generated frame reads as a design decision, which is the same false confidence as an unproven green"
  exit 1
fi
