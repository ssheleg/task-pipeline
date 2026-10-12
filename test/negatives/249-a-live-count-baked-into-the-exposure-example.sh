#!/usr/bin/env bash
# name: Negative self-test (a live count baked into the exposure example)
set -eu
rm -rf /tmp/ex2-copy && cp -R . /tmp/ex2-copy
python3 - <<'EOF'
p = "/tmp/ex2-copy/plugins/task-pipeline/skills/task-pipeline/references/exposure.md"
t = open(p, encoding="utf-8").read()
assert "exposure: N unverified" in t, "PLANT DID NOT LAND: the example line moved"
open(p, "w", encoding="utf-8").write(
    t.replace("exposure: N unverified", "exposure: 99 unverified", 1))
EOF
if python3 /tmp/ex2-copy/test/validate.py; then
  echo "ERROR: a live count in a doctrine is a count nobody updates"
  exit 1
else
  echo "OK: validator correctly FAILs — the worked example carries no digits"
fi
