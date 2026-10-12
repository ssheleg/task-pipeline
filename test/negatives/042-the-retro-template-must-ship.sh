#!/usr/bin/env bash
# name: Negative self-test (the retro template must ship)
set -eu
rm -rf /tmp/retro-tpl-copy && cp -R . /tmp/retro-tpl-copy
rm -f /tmp/retro-tpl-copy/plugins/task-pipeline/skills/task-pipeline/templates/retro.md
if python3 /tmp/retro-tpl-copy/test/validate.py; then
  echo "ERROR: validator passed with no retro template — the run has nowhere to write its lessons"
  exit 1
else
  echo "OK: validator requires the retro template"
fi
