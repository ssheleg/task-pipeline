#!/usr/bin/env bash
# name: Negative self-test (the header block drifting between its two copies)
set -eu
rm -rf /tmp/hdr-copy && cp -R . /tmp/hdr-copy
python3 - <<'EOF'
p = "/tmp/hdr-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
assert " · unlooked N" in t, "PLANT DID NOT LAND: the field is not in the block"
open(p, "w", encoding="utf-8").write(t.replace(" · unlooked N", "", 1))
EOF
if python3 /tmp/hdr-copy/test/validate.py; then
  echo "ERROR: one block, two copies, and a field silently in only one of them"
  exit 1
else
  echo "OK: validator correctly FAILs — both directions of the header field set"
fi
