#!/usr/bin/env bash
# name: Negative self-test (stage 0's own section must state the measured lag)
set -eu
rm -rf /tmp/gs02-copy && cp -R . /tmp/gs02-copy
python3 - <<'EOF'
p = "/tmp/gs02-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert t.count("measured lag") == 2, "PLANT DID NOT LAND: expected 2 needles before edit"
t = t.replace("measured lag", "build date")
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/gs02-copy/test/validate.py; then
  echo "ERROR: validator passed with stage 0's section no longer stating the measured lag"
  exit 1
else
  echo "OK: validator correctly FAILs — stage 0's own section must state the measured lag"
fi
