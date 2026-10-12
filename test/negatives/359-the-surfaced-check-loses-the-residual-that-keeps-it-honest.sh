#!/usr/bin/env bash
# name: Negative self-test (the SURFACED check loses the residual that keeps it honest)
set -eu
rm -rf /tmp/sf2-copy && cp -R . /tmp/sf2-copy
python3 - <<'EOF'
p = "/tmp/sf2-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
n = 'nothing will notice'
assert n in t, "PLANT DID NOT LAND: sf2"
_planted = t.replace(n, 'the run is done', 1)
assert _planted != t, "PLANT DID NOT LAND: sf2"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/sf2-copy/test/validate.py 2>&1 | grep -q 'lost its residual'; then
  echo "OK: validator FAILs — a check sold as more than it is buys false confidence"
else
  echo "ERROR: the check now reads as coverage it does not have"
  exit 1
fi
