#!/usr/bin/env bash
# name: Negative self-test (the exposure example drifting from its own print)
set -eu
rm -rf /tmp/ex1-copy && cp -R . /tmp/ex1-copy
python3 - <<'EOF'
p = "/tmp/ex1-copy/plugins/task-pipeline/skills/task-pipeline/references/exposure.md"
t = open(p, encoding="utf-8").read()
assert "releases carry one" in t, "PLANT DID NOT LAND: the third component moved"
open(p, "w", encoding="utf-8").write(
    t.replace("releases carry one", "releases since the last confirmation"))
EOF
if python3 /tmp/ex1-copy/test/validate.py; then
  echo "ERROR: the doctrine teaches a format the code has never printed"
  exit 1
else
  echo "OK: validator correctly FAILs — the example is computed from the print"
fi
