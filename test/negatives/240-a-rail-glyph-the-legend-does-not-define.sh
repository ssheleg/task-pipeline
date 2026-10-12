#!/usr/bin/env bash
# name: Negative self-test (a rail glyph the legend does not define)
set -eu
rm -rf /tmp/glyph-copy && cp -R . /tmp/glyph-copy
python3 - <<'EOF'
p = "/tmp/glyph-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
assert "3 ▶" in t, "PLANT DID NOT LAND: the rail's in-flight glyph moved"
open(p, "w", encoding="utf-8").write(t.replace("3 ▶", "3 »", 1))
EOF
if python3 /tmp/glyph-copy/test/validate.py; then
  echo "ERROR: the rail prints a symbol a reader has nothing to look up"
  exit 1
else
  echo "OK: validator correctly FAILs — every printed glyph is in the legend"
fi
