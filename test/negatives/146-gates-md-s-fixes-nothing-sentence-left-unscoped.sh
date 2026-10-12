#!/usr/bin/env bash
# name: Negative self-test (gates.md's fixes-nothing sentence left unscoped)
set -eu
rm -rf /tmp/ap3-copy && cp -R . /tmp/ap3-copy
python3 - <<'EOF'
# Both rules were true and neither was scoped, so a reader could take either as
# the whole rule — *the framework fixes nothing* and *the ladder is fixed*.
p = "/tmp/ap3-copy/plugins/task-pipeline/skills/task-pipeline/references/gates.md"
t = open(p, encoding="utf-8").read()
assert "**That sentence is about the pipeline's SHAPE" in t, "PLANT DID NOT LAND: anchor absent"
i = t.index("**That sentence is about the pipeline's SHAPE")
j = t.index("## The judgment gate", i)
open(p, "w", encoding="utf-8").write(t[:i] + t[j:])
assert "AP-1" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/ap3-copy/test/validate.py; then
  echo "ERROR: validator passed the two acceptance rules standing unscoped side by side"
  exit 1
else
  echo "OK: validator correctly FAILs — the scoping sentence is what makes the two readable together"
fi
