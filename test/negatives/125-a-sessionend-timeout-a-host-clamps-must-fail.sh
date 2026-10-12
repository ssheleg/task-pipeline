#!/usr/bin/env bash
# name: Negative self-test (a SessionEnd timeout a host clamps must fail)
set -eu
rm -rf /tmp/se3 && cp -R . /tmp/se3
python3 test/plant_sessionend_timeout.py /tmp/se3
if python3 /tmp/se3/test/validate.py; then
  echo "ERROR: validator passed with a SessionEnd timeout Codex clamps"; exit 1
else
  echo "OK: validator correctly FAILs — a SessionEnd timeout a host clamps"
fi
