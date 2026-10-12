#!/usr/bin/env bash
# name: Negative self-test (release.enabled true but workflow missing must fail)
set -eu
rm -rf /tmp/rel-copy && cp -R . /tmp/rel-copy
rm -f /tmp/rel-copy/.github/workflows/release.yml
if python3 /tmp/rel-copy/test/validate.py; then
  echo "ERROR: validator passed with release.enabled true but no release.yml"
  exit 1
else
  echo "OK: validator requires the release workflow when release is enabled"
fi
