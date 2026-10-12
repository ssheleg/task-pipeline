#!/usr/bin/env bash
# name: Negative self-test (the navigator must exist)
set -eu
rm -rf /tmp/ed1-copy && cp -R . /tmp/ed1-copy
python3 - <<'EOF'
import os
os.remove("/tmp/ed1-copy/plugins/task-pipeline/skills/evidence-docs/SKILL.md")
EOF
if python3 /tmp/ed1-copy/test/validate.py; then
  echo "ERROR: validator passed with the navigator must exist broken"
  exit 1
else
  echo "OK: validator correctly FAILs — the navigator must exist"
fi
