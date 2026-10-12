#!/usr/bin/env bash
# name: Negative self-test (the frame becomes a contract without a width)
set -eu
rm -rf /tmp/fig2-copy && cp -R . /tmp/fig2-copy
python3 - <<'EOF'
p = "/tmp/fig2-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
n = 'contract at its own width'
assert n in t, "PLANT DID NOT LAND: fig2"
_planted = t.replace(n, 'contract', 1)
assert _planted != t, "PLANT DID NOT LAND: fig2"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fig2-copy/test/validate.py 2>&1 | grep -q 'without its'; then
  echo "OK: validator FAILs — a frame is one width and said nothing about the others"
else
  echo "ERROR: a rule that cannot be followed at any other breakpoint shipped as if it could"
  exit 1
fi
