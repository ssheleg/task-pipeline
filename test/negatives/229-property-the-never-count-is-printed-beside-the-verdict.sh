#!/usr/bin/env bash
# name: Property check (the never-count is printed beside the verdict)
set -eu
rm -rf /tmp/vf7-copy && cp -R . /tmp/vf7-copy
out=$(python3 /tmp/vf7-copy/test/validate.py) || { echo "ERROR: validator failed for an unrelated reason"; exit 1; }
if printf '%s' "$out" | grep -q "never confirmed by a person"; then
  echo "OK: the count is surfaced — a measurement nobody prints is the same silence as no measurement"
else
  echo "ERROR: the never-count is computed and dropped on the floor"
  exit 1
fi
