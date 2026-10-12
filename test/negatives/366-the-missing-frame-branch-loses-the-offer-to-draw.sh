#!/usr/bin/env bash
# name: Negative self-test (the missing-frame branch loses the offer to draw)
set -eu
rm -rf /tmp/fig3-copy && cp -R . /tmp/fig3-copy
python3 - <<'EOF'
p = "/tmp/fig3-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
n = 'offers to draw'
assert n in t, "PLANT DID NOT LAND: fig3"
_planted = t.replace(n, 'mentions', 1)
assert _planted != t, "PLANT DID NOT LAND: fig3"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fig3-copy/test/validate.py 2>&1 | grep -q 'lost a half'; then
  echo "OK: validator FAILs — building and naming without offering leaves the file drifting"
else
  echo "ERROR: the design file drifts from the product with nobody proposing to close it"
  exit 1
fi
