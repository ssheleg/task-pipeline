#!/usr/bin/env bash
# name: Negative self-test (the doc map must carry its propagation matrix)
set -eu
rm -rf /tmp/docmap-copy && cp -R . /tmp/docmap-copy
python3 - <<'EOF'
p = "/tmp/docmap-copy/plugins/task-pipeline/skills/task-pipeline/templates/docmap.md"
t = open(p, encoding="utf-8").read()
assert "## Propagation matrix" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("## Propagation matrix", "## What changes what", 1))
EOF
if python3 /tmp/docmap-copy/test/validate.py; then
  echo "ERROR: validator passed a doc map with no propagation matrix — that seeds a project with a register and no obligation"
  exit 1
else
  echo "OK: validator requires the doc map's propagation matrix"
fi
