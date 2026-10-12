#!/usr/bin/env bash
# name: Negative self-test (the grill doctrine must ship with the skill)
set -eu
rm -rf /tmp/doctrine-copy && cp -R . /tmp/doctrine-copy
rm -f /tmp/doctrine-copy/plugins/task-pipeline/skills/task-pipeline/references/grill.md
if python3 /tmp/doctrine-copy/test/validate.py; then
  echo "ERROR: validator passed without the built-in grill doctrine"
  exit 1
else
  echo "OK: validator requires references/grill.md — the grill is built in, not a dependency"
fi
