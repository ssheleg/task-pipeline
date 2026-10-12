#!/usr/bin/env bash
# name: Negative self-test (hardcoded vendor model id must fail)
set -eu
rm -rf /tmp/model-copy && cp -R . /tmp/model-copy
printf '\nSwitch with `/model claude-opus-5` first.\n' \
  >> /tmp/model-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md
if python3 /tmp/model-copy/test/validate.py; then
  echo "ERROR: validator passed a hardcoded model id — ids go stale, the tier is the contract"
  exit 1
else
  echo "OK: validator rejects a hardcoded model id"
fi
