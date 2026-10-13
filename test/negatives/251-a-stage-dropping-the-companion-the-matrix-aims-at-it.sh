#!/usr/bin/env bash
# name: Negative self-test (a stage dropping the companion the matrix aims at it)
set -eu
rm -rf /tmp/cw2-copy && cp -R . /tmp/cw2-copy
python3 - <<'EOF'
p = "/tmp/cw2-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-03-spec.md"
t = open(p, encoding="utf-8").read()
assert "`sheleg-design`" in t, "PLANT DID NOT LAND: the visual companion moved"
open(p, "w", encoding="utf-8").write(t.replace("`sheleg-design`", "the visual skill"))
EOF
if python3 /tmp/cw2-copy/test/validate.py; then
  echo "ERROR: a recommended companion no stage names is a recommendation for the reader only"
  exit 1
else
  echo "OK: validator correctly FAILs — the stage names its own companions"
fi
