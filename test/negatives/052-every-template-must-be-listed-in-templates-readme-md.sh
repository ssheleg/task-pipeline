#!/usr/bin/env bash
# name: Negative self-test (every template must be listed in templates/README.md)
set -eu
rm -rf /tmp/tplreadme-copy && cp -R . /tmp/tplreadme-copy
echo "# stray" > /tmp/tplreadme-copy/plugins/task-pipeline/skills/task-pipeline/templates/unlisted.md
if python3 /tmp/tplreadme-copy/test/validate.py; then
  echo "ERROR: validator passed an unlisted template — one nobody knows to seed"
  exit 1
else
  echo "OK: validator requires templates/README.md to list every template"
fi
