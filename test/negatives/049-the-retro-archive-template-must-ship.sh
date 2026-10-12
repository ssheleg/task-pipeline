#!/usr/bin/env bash
# name: Negative self-test (the retro archive template must ship)
set -eu
rm -rf /tmp/retroarch-copy && cp -R . /tmp/retroarch-copy
rm /tmp/retroarch-copy/plugins/task-pipeline/skills/task-pipeline/templates/retro-archive.md
if python3 /tmp/retroarch-copy/test/validate.py; then
  echo "ERROR: validator passed with no archive template — the in-force retro is capped and read in full, so its history needs a home"
  exit 1
else
  echo "OK: validator requires templates/retro-archive.md"
fi
