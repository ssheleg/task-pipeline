#!/usr/bin/env bash
# name: Negative self-test (the short path marking a stage with an undefined glyph)
set -eu
rm -rf /tmp/sp-copy && cp -R . /tmp/sp-copy
python3 - <<'EOF'
p = "/tmp/sp-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-00-intake.md"
t = open(p, encoding="utf-8").read()
needle = "print `⊘`"
assert needle in t, "PLANT DID NOT LAND: the short path's glyph moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "print `※`", 1))
EOF
if python3 /tmp/sp-copy/test/validate.py; then
  echo "ERROR: a skipped stage marked with a symbol no legend defines"
  exit 1
else
  echo "OK: validator correctly FAILs — every skip glyph is in the legend"
fi
