#!/usr/bin/env bash
# name: Negative self-test (the documentation-track doctrine must ship)
set -eu
for f in documentation gates hooks; do
  rm -rf /tmp/doctrine-copy-2 && cp -R . /tmp/doctrine-copy-2
  rm /tmp/doctrine-copy-2/plugins/task-pipeline/skills/task-pipeline/references/$f.md
  if python3 /tmp/doctrine-copy-2/test/validate.py; then
    echo "ERROR: validator passed with references/$f.md missing"
    exit 1
  fi
done
echo "OK: validator requires documentation.md, gates.md and hooks.md"
