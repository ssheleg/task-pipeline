#!/usr/bin/env bash
# name: Property check (the cross-commit skip is printed, never swallowed)
set -eu
rm -rf /tmp/hw5-copy && cp -R . /tmp/hw5-copy && rm -rf /tmp/hw5-copy/.git
out=$(python3 /tmp/hw5-copy/test/validate.py) || { echo "ERROR: validator failed for an unrelated reason"; exit 1; }
if printf '%s' "$out" | grep -q "high-water mark vs its own history"; then
  echo "OK: outside a checkout the skip is printed as an unlooked disclosure, not swallowed"
else
  echo "ERROR: the check could not run and said nothing — a silent skip reads as a pass"
  exit 1
fi
