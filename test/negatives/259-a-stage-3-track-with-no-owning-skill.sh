#!/usr/bin/env bash
# name: Negative self-test (a stage-3 track with no owning skill)
set -eu
rm -rf /tmp/trk1-copy && cp -R . /tmp/trk1-copy
python3 - <<'EOF'
p = "/tmp/trk1-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert "`copywriting`" in t, "PLANT DID NOT LAND: the copy companion moved"
open(p, "w", encoding="utf-8").write(t.replace("`copywriting`", "the writing skill"))
EOF
if python3 /tmp/trk1-copy/test/validate.py; then
  echo "ERROR: a track heading with no skill behind it — which is what the copy half was for a year"
  exit 1
else
  echo "OK: validator correctly FAILs — every stage-3 track names its owner"
fi
