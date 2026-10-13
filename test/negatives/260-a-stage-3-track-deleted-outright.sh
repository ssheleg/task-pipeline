#!/usr/bin/env bash
# name: Negative self-test (a stage-3 track deleted outright)
set -eu
rm -rf /tmp/trk2-copy && cp -R . /tmp/trk2-copy
python3 - <<'EOF'
import re
p = "/tmp/trk2-copy/plugins/task-pipeline/skills/task-pipeline/references/stage-03-spec.md"
t = open(p, encoding="utf-8").read()
# Case-insensitive on purpose. The first version replaced only the heading's
# SHOUTED form and left "ends the visual track" in the refusal sentence, so
# the guard kept finding the track and stayed correctly quiet — a probe that
# deletes one spelling of a phrase and calls the class removed.
n, k = re.subn(r"visual track", "look-and-feel pass", t, flags=re.I)
assert k >= 2, "PLANT DID NOT LAND: the visual track is spelled fewer ways than expected"
open(p, "w", encoding="utf-8").write(n)
EOF
if python3 /tmp/trk2-copy/test/validate.py; then
  echo "ERROR: the stage names what the interface must do and not how it looks"
  exit 1
else
  echo "OK: validator correctly FAILs — all three tracks are named at stage 3"
fi
