#!/usr/bin/env bash
# name: Negative self-test (the routing rule must ship as a file)
set -eu
rm -rf /tmp/rule-copy && cp -R . /tmp/rule-copy
rm /tmp/rule-copy/plugins/task-pipeline/skills/task-pipeline/templates/routing-rule.md
if python3 /tmp/rule-copy/test/validate.py; then
  echo "ERROR: validator passed with the routing rule hand-installed only — it would not travel with the bundle"
  exit 1
else
  echo "OK: the routing default ships as a template"
fi
