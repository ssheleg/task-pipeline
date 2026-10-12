#!/usr/bin/env bash
# name: Negative self-test (a restated count of gates.md's own axes)
set -eu
rm -rf /tmp/axis4-copy && cp -R . /tmp/axis4-copy
python3 - <<'EOF'
p = "/tmp/axis4-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
needle = "# Gates — the three axes,"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "# Gates — the two axes,", 1))
assert "the two axes" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/axis4-copy/test/validate.py; then
  echo "ERROR: validator passed a title claiming two axes over a file with three"
  exit 1
else
  echo "OK: validator correctly FAILs — the count is computed from the Axis headings"
fi
