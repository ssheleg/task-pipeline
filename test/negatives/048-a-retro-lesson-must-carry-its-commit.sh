#!/usr/bin/env bash
# name: Negative self-test (a retro lesson must carry its commit)
set -eu
rm -rf /tmp/retrocommit-copy && cp -R . /tmp/retrocommit-copy
python3 - <<'EOF'
p = "/tmp/retrocommit-copy/plugins/task-pipeline/skills/task-pipeline/templates/retro.md"
t = open(p, encoding="utf-8").read()
assert "Commit" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("Commit", "Ref"))
EOF
if python3 /tmp/retrocommit-copy/test/validate.py; then
  echo "ERROR: validator passed a retro with no Commit column — file:line evidence rots at the next edit"
  exit 1
else
  echo "OK: validator requires the retro's commit columns"
fi
