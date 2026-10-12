#!/usr/bin/env bash
# name: Negative self-test (a moved component pointer needing no convergence record)
set -eu
rm -rf /tmp/cnv1-copy && cp -R . /tmp/cnv1-copy
python3 - <<'EOF'
p = "/tmp/cnv1-copy/plugins/task-pipeline/skills/task-pipeline/templates/convergence.sh"
t = open(p, encoding="utf-8").read()
needle = 'bad "$c: its pointer moved and no convergence record exists'
assert needle in t, "PLANT DID NOT LAND: cnv1 — the seam requirement moved"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'ok "$c: moved"; : "', 1))
EOF
if python3 /tmp/cnv1-copy/test/validate.py; then
  echo "ERROR: a moved component pointer with no convergence record was accepted —
         B-087: the pointer proves commits, and the composition at those versions
         was never observed"; exit 1
else
  echo "OK: convergence.sh is executed over real repositories, seam included"
fi
