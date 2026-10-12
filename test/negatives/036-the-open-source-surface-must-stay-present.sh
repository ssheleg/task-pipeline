#!/usr/bin/env bash
# name: Negative self-test (the open-source surface must stay present)
set -eu
rm -rf /tmp/oss-copy && cp -R . /tmp/oss-copy
rm -f /tmp/oss-copy/CONTRIBUTING.md
if python3 /tmp/oss-copy/test/validate.py; then
  echo "ERROR: validator passed a repo with no CONTRIBUTING.md"
  exit 1
else
  echo "OK: validator requires the open-source root files"
fi
