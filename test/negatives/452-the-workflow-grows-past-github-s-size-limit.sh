#!/usr/bin/env bash
# name: Negative self-test (the workflow grows past GitHub's size limit)
set -eu
rm -rf /tmp/wfsz-copy && cp -R . /tmp/wfsz-copy
python3 - <<'EOF'
# Past 512,000 bytes GitHub creates no runs at all and reports the workflow
# `active` — measured 2026-09-05. The guard had no plant while the workflow sat
# 4 KB under the line; with the checks moved out it sits far under, so the
# only way to watch it fire is to push a copy over.
import os
p = "/tmp/wfsz-copy/.github/workflows/validate.yml"
t = open(p, encoding="utf-8").read()
line = "# padding: a plant written inline, many times over\n"
need = 512_001 - len(t.encode("utf-8"))
open(p, "w", encoding="utf-8").write(t + line * (need // len(line) + 1))
assert os.path.getsize(p) > 512_000, "PLANT DID NOT LAND: the copy is still under the limit"
EOF
if python3 /tmp/wfsz-copy/test/validate.py 2>&1 | grep -q "past GitHub's"; then
  echo "OK: validator FAILs — the workflow size is a budget, refused before GitHub goes silent"
else
  echo "ERROR: the workflow passed GitHub's size limit and the gate said nothing"
  exit 1
fi
