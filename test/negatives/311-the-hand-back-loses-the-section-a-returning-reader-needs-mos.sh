#!/usr/bin/env bash
# name: Negative self-test (the hand-back loses the section a returning reader needs most)
set -eu
rm -rf /tmp/hb01-copy && cp -R . /tmp/hb01-copy
python3 - <<'EOF'
p = "/tmp/hb01-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
n = "SURFACED    what came up that nobody asked for"
assert n in t, "PLANT DID NOT LAND: hb01"
open(p, "w", encoding="utf-8").write(t.replace(n, "EXTRAS      anything else worth a line", 1))
EOF
if python3 /tmp/hb01-copy/test/validate.py 2>&1 | grep -q 'the .SURFACED. section is gone'; then
  echo "OK: validator FAILs — what a run learned by accident is recoverable from no artefact"
else
  echo "ERROR: the hand-back lost SURFACED and nothing objected"
  exit 1
fi
