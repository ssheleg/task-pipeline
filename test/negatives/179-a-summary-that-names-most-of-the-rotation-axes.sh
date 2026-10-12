#!/usr/bin/env bash
# name: Negative self-test (a summary that names most of the rotation axes)
set -eu
rm -rf /tmp/axis1-copy && cp -R . /tmp/axis1-copy
python3 - <<'EOF'
p = "/tmp/axis1-copy/cursor/rules/task-pipeline.mdc"
t = open(p, encoding="utf-8").read()
needle = ", then **false success** (not \"is this\n  check correct\" but \"what does this mechanism print when it did not look?\"), then\n  **re-derivation**"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
t = t.replace(needle, ", then\n  **re-derivation**", 1)
open(p, "w", encoding="utf-8").write(t)
assert "false success" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis1-copy/test/validate.py; then
  echo "ERROR: validator passed an enumeration missing an axis — the drift this guard exists for"
  exit 1
else
  echo "OK: validator correctly FAILs — a surface that enumerates the axes names all of them"
fi
