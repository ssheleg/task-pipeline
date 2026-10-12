#!/usr/bin/env bash
# name: Negative self-test (the audit doctrine must ship with the skill)
set -eu
rm -rf /tmp/audit-copy && cp -R . /tmp/audit-copy
rm -f /tmp/audit-copy/plugins/task-pipeline/skills/task-pipeline/references/audit.md
if python3 /tmp/audit-copy/test/validate.py; then
  echo "ERROR: validator passed without the built-in audit doctrine"
  exit 1
else
  echo "OK: validator requires references/audit.md"
fi
