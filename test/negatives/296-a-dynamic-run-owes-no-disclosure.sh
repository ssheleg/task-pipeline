#!/usr/bin/env bash
# name: Negative self-test (a dynamic run owes no disclosure)
set -eu
rm -rf /tmp/lp06-copy && cp -R . /tmp/lp06-copy
python3 - <<'EOF'
p = "/tmp/lp06-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
n = 'prints **the delay it chose and why**'
assert n in t, "PLANT DID NOT LAND: lp06"
open(p, "w", encoding="utf-8").write(t.replace(n, 'runs quietly', 1))
EOF
if python3 /tmp/lp06-copy/test/validate.py 2>&1 | grep -q 'never says a self-pacing run prints the delay'; then
  echo "OK: validator FAILs — a run silent about its pacing looks like one that stopped"
else
  echo "ERROR: the dynamic disclosure vanished and nothing objected"
  exit 1
fi
