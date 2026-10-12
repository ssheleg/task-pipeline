#!/usr/bin/env bash
# name: Negative self-test (no stage naming the publish step)
set -eu
rm -rf /tmp/rp7-copy && cp -R . /tmp/rp7-copy
python3 - <<'EOF'
p = "/tmp/rp7-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert "`retro.publish`" in t, "PLANT DID NOT LAND: the stage reference moved"
open(p, "w", encoding="utf-8").write(t.replace("`retro.publish`", "the publish setting"))
EOF
if python3 /tmp/rp7-copy/test/validate.py; then
  echo "ERROR: a step in the retro's doctrine and in no stage is a step that never runs"
  exit 1
else
  echo "OK: validator correctly FAILs — the outward step is named by a stage"
fi
